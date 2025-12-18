#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
永续合约价格线和RSI监控工具 - Kivy安卓版本

使用Kivy框架开发，可以打包成APK在安卓手机上运行
支持GUI界面配置监控参数
支持后台运行和通知提醒
"""

import time
from datetime import datetime
import threading
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import numpy as np

# Kivy imports
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.checkbox import CheckBox
from kivy.uix.scrollview import ScrollView
from kivy.clock import Clock, mainthread
from kivy.properties import StringProperty, BooleanProperty
from kivy.core.audio import SoundLoader
from kivy.core.text import LabelBase
from kivy.resources import resource_add_path
from kivy.lang import Builder
import os

# 安卓特定功能（仅在安卓上可用）
try:
    from android.permissions import request_permissions, Permission
    from android.runnable import run_on_ui_thread
    from plyer import notification, vibrator, tts
    ANDROID = True
except ImportError:
    ANDROID = False
    print("警告: 非安卓环境，某些功能不可用")

# TTS语音引擎
try:
    import pyttsx3
    DESKTOP_TTS_AVAILABLE = True
except ImportError:
    DESKTOP_TTS_AVAILABLE = False
    print("警告: pyttsx3未安装，桌面语音功能不可用")


class MonitorConfig:
    """监控配置"""
    def __init__(self):
        # 多合约和多周期支持
        self.symbols = ['ETHUSDT']  # 默认监控ETHUSDT
        self.timeframes = ['3m']     # 默认3分钟周期
        self.limit = 100

        # 价格线阈值
        self.price_line_low = 23.0
        self.price_line_high = 75.0

        # RSI阈值
        self.rsi_low = 23.0
        self.rsi_high = 75.0

        # 监控间隔（秒）
        self.check_interval = 15

        # API请求配置
        self.max_retries = 3
        self.retry_delay = 2
        self.request_timeout = 10
        self.min_request_interval = 1.0


class BinanceAPIClient:
    """币安API客户端"""

    def __init__(self, config):
        self.config = config
        self.base_url = "https://api.binance.com"
        self.session = self._create_session()
        self.request_count = 0
        self.failed_count = 0
        self.last_request_time = 0

    def _create_session(self):
        """创建带重试策略的Session"""
        session = requests.Session()
        retry_strategy = Retry(
            total=self.config.max_retries,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET"]
        )
        adapter = HTTPAdapter(
            max_retries=retry_strategy,
            pool_connections=1,
            pool_maxsize=1,
            pool_block=False
        )
        session.mount("https://", adapter)
        session.mount("http://", adapter)
        return session

    def _wait_for_rate_limit(self):
        """等待以满足速率限制"""
        current_time = time.time()
        elapsed = current_time - self.last_request_time
        if elapsed < self.config.min_request_interval:
            time.sleep(self.config.min_request_interval - elapsed)
        self.last_request_time = time.time()

    def fetch_klines(self, symbol, timeframe):
        """获取K线数据"""
        url = f"{self.base_url}/api/v3/klines"
        params = {
            'symbol': symbol,
            'interval': timeframe,
            'limit': self.config.limit
        }

        retry_count = 0
        last_error = None

        while retry_count <= self.config.max_retries:
            try:
                self._wait_for_rate_limit()
                response = self.session.get(url, params=params, timeout=self.config.request_timeout)
                self.request_count += 1

                if response.status_code == 200:
                    data = response.json()
                    if data and len(data) > 0:
                        return True, data, None
                    else:
                        return False, None, "返回数据为空"
                elif response.status_code == 429:
                    retry_after = int(response.headers.get('Retry-After', 60))
                    time.sleep(retry_after)
                    retry_count += 1
                    continue
                else:
                    retry_count += 1
                    time.sleep(self.config.retry_delay)

            except Exception as e:
                retry_count += 1
                last_error = str(e)
                time.sleep(self.config.retry_delay)

        self.failed_count += 1
        return False, None, f"请求失败: {last_error}"

    def close(self):
        """关闭Session"""
        try:
            if hasattr(self, 'session') and self.session:
                self.session.close()
        except:
            pass


class PriceLineCalculator:
    """价格线计算器"""

    def __init__(self, api_client, config):
        self.api_client = api_client
        self.config = config
        self.dates = []
        self.highs = []
        self.lows = []
        self.closes = []
        self.hhv_period = 33
        self.sma_period = 8
        self.hhv_a_period = 3

    def fetch_kline_data(self, symbol, timeframe):
        """从币安获取K线数据"""
        success, data, error = self.api_client.fetch_klines(symbol, timeframe)
        if not success:
            return False, error

        self.dates = []
        self.highs = []
        self.lows = []
        self.closes = []

        for kline in data:
            timestamp = kline[0]
            high_price = float(kline[2])
            low_price = float(kline[3])
            close_price = float(kline[4])

            self.dates.append(datetime.fromtimestamp(timestamp / 1000).strftime('%Y-%m-%d %H:%M:%S'))
            self.highs.append(high_price)
            self.lows.append(low_price)
            self.closes.append(close_price)

        if len(self.closes) < self.hhv_period + self.sma_period + self.hhv_a_period:
            return False, "数据不足"

        return True, None

    def tdx_sma(self, data, period, weight=1):
        """通达信SMA函数"""
        if len(data) == 0:
            return []
        sma_values = []
        sma = data[0]
        for i in range(len(data)):
            sma = (weight * data[i] + (period - weight) * sma) / period
            sma_values.append(sma)
        return sma_values

    def ema(self, data, period):
        """标准EMA函数"""
        if len(data) == 0:
            return []
        alpha = 2.0 / (period + 1)
        ema_values = []
        ema = data[0]
        for i in range(len(data)):
            ema = alpha * data[i] + (1 - alpha) * ema
            ema_values.append(ema)
        return ema_values

    def calculate_price_line(self):
        """计算价格线指标"""
        if len(self.closes) < self.hhv_period:
            return None

        rsv_values = []
        for i in range(self.hhv_period - 1, len(self.closes)):
            var1 = max(self.highs[i - self.hhv_period + 1:i + 1])
            var2 = min(self.lows[i - self.hhv_period + 1:i + 1])

            if var1 - var2 == 0:
                rsv = 0
            else:
                rsv = (self.closes[i] - var2) / (var1 - var2)
            rsv_values.append(rsv)

        sma_values = self.tdx_sma(rsv_values, self.sma_period, 1)
        a_values = [x * 100 for x in sma_values]

        # 计算 HHV(A, 3)
        hhv_a_values = []
        for i in range(len(a_values)):
            if i < self.hhv_a_period - 1:
                hhv_a = max(a_values[0:i + 1])
            else:
                hhv_a = max(a_values[i - self.hhv_a_period + 1:i + 1])
            hhv_a_values.append(hhv_a)

        # 应用 EMA(HHV(A, 3), 1)
        price_line_values = self.ema(hhv_a_values, 1)
        return price_line_values[-1] if price_line_values else None


class RSICalculator:
    """RSI计算器"""

    @staticmethod
    def calculate_rsi(prices, period=6):
        """使用Wilder's平滑法计算RSI"""
        if len(prices) < period + 1:
            return None

        deltas = np.diff(prices)
        gains = np.where(deltas > 0, deltas, 0)
        losses = np.where(deltas < 0, -deltas, 0)

        avg_gain = np.mean(gains[:period])
        avg_loss = np.mean(losses[:period])

        for i in range(period, len(gains)):
            avg_gain = (avg_gain * (period - 1) + gains[i]) / period
            avg_loss = (avg_loss * (period - 1) + losses[i]) / period

        if avg_loss == 0:
            return 100.0

        rs = avg_gain / avg_loss
        rsi = 100.0 - (100.0 / (1.0 + rs))
        return rsi


class TTSManager:
    """跨平台语音播报管理器"""

    def __init__(self):
        self.tts_engine = None
        self.is_available = False
        self.is_speaking = False

        # 初始化TTS引擎
        if ANDROID:
            # Android使用plyer的TTS
            try:
                self.is_available = True
                print("Android TTS已初始化")
            except Exception as e:
                print(f"Android TTS初始化失败: {e}")
        elif DESKTOP_TTS_AVAILABLE:
            # 桌面平台使用pyttsx3
            try:
                self.tts_engine = pyttsx3.init()

                # 配置语音参数
                self.tts_engine.setProperty('rate', 150)  # 语速
                self.tts_engine.setProperty('volume', 1.0)  # 音量

                # 尝试设置中文语音
                voices = self.tts_engine.getProperty('voices')
                chinese_voice = None

                for voice in voices:
                    # macOS中文语音包含 'zh' 或 'Chinese'
                    if 'zh' in voice.id.lower() or 'chinese' in voice.name.lower():
                        chinese_voice = voice
                        break

                if chinese_voice:
                    self.tts_engine.setProperty('voice', chinese_voice.id)
                    print(f"已设置中文语音: {chinese_voice.name}")
                else:
                    print("未找到中文语音，将使用系统默认语音")

                self.is_available = True
                print("桌面TTS已初始化")
            except Exception as e:
                print(f"桌面TTS初始化失败: {e}")
                self.is_available = False

    def speak(self, text):
        """播报文本"""
        if not self.is_available or self.is_speaking:
            return

        self.is_speaking = True

        try:
            if ANDROID:
                # Android TTS（异步）
                tts.speak(text)
            elif self.tts_engine:
                # 桌面TTS（同步，在后台线程运行）
                import threading
                def speak_thread():
                    try:
                        self.tts_engine.say(text)
                        self.tts_engine.runAndWait()
                    finally:
                        self.is_speaking = False

                thread = threading.Thread(target=speak_thread, daemon=True)
                thread.start()
                return  # 异步执行，不阻塞
        except Exception as e:
            print(f"TTS播报错误: {e}")

        self.is_speaking = False

    def stop(self):
        """停止播报"""
        if self.tts_engine and hasattr(self.tts_engine, 'stop'):
            try:
                self.tts_engine.stop()
            except:
                pass
        self.is_speaking = False


class MonitorWidget(BoxLayout):
    """监控界面主Widget"""

    status_text = StringProperty("等待启动...")
    is_monitoring = BooleanProperty(False)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = 8
        self.spacing = 6

        self.config = MonitorConfig()
        self.api_client = None
        self.monitor_thread = None
        self.stop_monitoring = False

        # 初始化TTS语音引擎
        self.tts_manager = TTSManager()

        self.build_ui()

    def build_ui(self):
        """构建用户界面"""

        # 标题
        title = Label(
            text='永续合约监控工具',
            size_hint_y=None,
            height=40,
            font_size='18sp',
            bold=True
        )
        self.add_widget(title)

        # 配置面板
        config_layout = GridLayout(cols=2, spacing=8, size_hint_y=None, height=210, row_default_height=35)

        # 价格线低位
        config_layout.add_widget(Label(text='价格线低位 (<=):', size_hint_y=None, height=35))
        self.price_line_low_input = TextInput(
            text=str(self.config.price_line_low),
            multiline=False,
            input_filter='float',
            size_hint_y=None,
            height=35
        )
        config_layout.add_widget(self.price_line_low_input)

        # 价格线高位
        config_layout.add_widget(Label(text='价格线高位 (>=):', size_hint_y=None, height=35))
        self.price_line_high_input = TextInput(
            text=str(self.config.price_line_high),
            multiline=False,
            input_filter='float',
            size_hint_y=None,
            height=35
        )
        config_layout.add_widget(self.price_line_high_input)

        # RSI低位
        config_layout.add_widget(Label(text='RSI(6)低位 (<=):', size_hint_y=None, height=35))
        self.rsi_low_input = TextInput(
            text=str(self.config.rsi_low),
            multiline=False,
            input_filter='float',
            size_hint_y=None,
            height=35
        )
        config_layout.add_widget(self.rsi_low_input)

        # RSI高位
        config_layout.add_widget(Label(text='RSI(6)高位 (>=):', size_hint_y=None, height=35))
        self.rsi_high_input = TextInput(
            text=str(self.config.rsi_high),
            multiline=False,
            input_filter='float',
            size_hint_y=None,
            height=35
        )
        config_layout.add_widget(self.rsi_high_input)

        # 监控间隔
        config_layout.add_widget(Label(text='监控间隔(秒):', size_hint_y=None, height=35))
        self.interval_input = TextInput(
            text=str(self.config.check_interval),
            multiline=False,
            input_filter='int',
            size_hint_y=None,
            height=35
        )
        config_layout.add_widget(self.interval_input)

        self.add_widget(config_layout)

        # 合约品种选择
        symbol_section = BoxLayout(orientation='vertical', size_hint_y=None, height=50, spacing=3)
        symbol_label = Label(text='监控品种:', size_hint_y=None, height=22, font_size='13sp', bold=True)
        symbol_section.add_widget(symbol_label)

        symbol_checkboxes = BoxLayout(size_hint_y=None, height=25, spacing=15)

        # ETHUSDT checkbox
        eth_box = BoxLayout(size_hint_x=None, width=150, spacing=5)
        self.eth_checkbox = CheckBox(active=True, size_hint_x=None, width=30)
        eth_box.add_widget(self.eth_checkbox)
        eth_box.add_widget(Label(text='ETHUSDT', size_hint_x=None, width=110))
        symbol_checkboxes.add_widget(eth_box)

        # BTCUSDT checkbox
        btc_box = BoxLayout(size_hint_x=None, width=150, spacing=5)
        self.btc_checkbox = CheckBox(active=False, size_hint_x=None, width=30)
        btc_box.add_widget(self.btc_checkbox)
        btc_box.add_widget(Label(text='BTCUSDT', size_hint_x=None, width=110))
        symbol_checkboxes.add_widget(btc_box)

        symbol_section.add_widget(symbol_checkboxes)
        self.add_widget(symbol_section)

        # K线周期选择
        timeframe_section = BoxLayout(orientation='vertical', size_hint_y=None, height=50, spacing=3)
        timeframe_label = Label(text='K线周期:', size_hint_y=None, height=22, font_size='13sp', bold=True)
        timeframe_section.add_widget(timeframe_label)

        timeframe_checkboxes = BoxLayout(size_hint_y=None, height=25, spacing=10)

        # 1m checkbox
        tf_1m_box = BoxLayout(size_hint_x=None, width=80, spacing=5)
        self.tf_1m_checkbox = CheckBox(active=False, size_hint_x=None, width=30)
        tf_1m_box.add_widget(self.tf_1m_checkbox)
        tf_1m_box.add_widget(Label(text='1m', size_hint_x=None, width=40))
        timeframe_checkboxes.add_widget(tf_1m_box)

        # 3m checkbox
        tf_3m_box = BoxLayout(size_hint_x=None, width=80, spacing=5)
        self.tf_3m_checkbox = CheckBox(active=True, size_hint_x=None, width=30)
        tf_3m_box.add_widget(self.tf_3m_checkbox)
        tf_3m_box.add_widget(Label(text='3m', size_hint_x=None, width=40))
        timeframe_checkboxes.add_widget(tf_3m_box)

        # 5m checkbox
        tf_5m_box = BoxLayout(size_hint_x=None, width=80, spacing=5)
        self.tf_5m_checkbox = CheckBox(active=False, size_hint_x=None, width=30)
        tf_5m_box.add_widget(self.tf_5m_checkbox)
        tf_5m_box.add_widget(Label(text='5m', size_hint_x=None, width=40))
        timeframe_checkboxes.add_widget(tf_5m_box)

        # 15m checkbox
        tf_15m_box = BoxLayout(size_hint_x=None, width=80, spacing=5)
        self.tf_15m_checkbox = CheckBox(active=False, size_hint_x=None, width=30)
        tf_15m_box.add_widget(self.tf_15m_checkbox)
        tf_15m_box.add_widget(Label(text='15m', size_hint_x=None, width=40))
        timeframe_checkboxes.add_widget(tf_15m_box)

        # 1d checkbox
        tf_1d_box = BoxLayout(size_hint_x=None, width=80, spacing=5)
        self.tf_1d_checkbox = CheckBox(active=False, size_hint_x=None, width=30)
        tf_1d_box.add_widget(self.tf_1d_checkbox)
        tf_1d_box.add_widget(Label(text='1d', size_hint_x=None, width=40))
        timeframe_checkboxes.add_widget(tf_1d_box)

        timeframe_section.add_widget(timeframe_checkboxes)
        self.add_widget(timeframe_section)

        # 控制按钮
        button_layout = BoxLayout(size_hint_y=None, height=50, spacing=10)

        self.start_button = Button(
            text='启动监控',
            background_color=(0.22, 0.69, 0.38, 1)  # 现代绿色 #38b058
        )
        self.start_button.bind(on_press=self.start_monitoring)
        button_layout.add_widget(self.start_button)

        self.stop_button = Button(
            text='停止监控',
            background_color=(0.86, 0.28, 0.29, 1),  # 现代红色 #db4748
            disabled=True
        )
        self.stop_button.bind(on_press=self.stop_monitoring_action)
        button_layout.add_widget(self.stop_button)

        self.add_widget(button_layout)

        # 状态显示区域
        status_label = Label(
            text='运行状态:',
            size_hint_y=None,
            height=25,
            font_size='15sp',
            bold=True
        )
        self.add_widget(status_label)

        # 滚动日志
        scroll = ScrollView(size_hint=(1, 1))
        self.log_label = Label(
            text=self.status_text,
            size_hint_y=None,
            text_size=(self.width - 20, None),
            halign='left',
            valign='top',
            markup=True  # 启用markup支持颜色
        )
        self.log_label.bind(texture_size=self.log_label.setter('size'))
        self.log_label.bind(text=self.on_log_text_change)
        scroll.add_widget(self.log_label)
        self.add_widget(scroll)

    def on_log_text_change(self, instance, value):
        """日志文本改变时调整大小"""
        instance.text_size = (self.width - 20, None)

    def update_config_from_ui(self):
        """从UI更新配置"""
        try:
            self.config.price_line_low = float(self.price_line_low_input.text)
            self.config.price_line_high = float(self.price_line_high_input.text)
            self.config.rsi_low = float(self.rsi_low_input.text)
            self.config.rsi_high = float(self.rsi_high_input.text)
            self.config.check_interval = int(self.interval_input.text)

            # 从checkbox读取选择的品种
            self.config.symbols = []
            if self.eth_checkbox.active:
                self.config.symbols.append('ETHUSDT')
            if self.btc_checkbox.active:
                self.config.symbols.append('BTCUSDT')

            # 从checkbox读取选择的周期
            self.config.timeframes = []
            if self.tf_1m_checkbox.active:
                self.config.timeframes.append('1m')
            if self.tf_3m_checkbox.active:
                self.config.timeframes.append('3m')
            if self.tf_5m_checkbox.active:
                self.config.timeframes.append('5m')
            if self.tf_15m_checkbox.active:
                self.config.timeframes.append('15m')
            if self.tf_1d_checkbox.active:
                self.config.timeframes.append('1d')

            # 验证至少选择了一个品种和一个周期
            if not self.config.symbols:
                self.append_log("错误: 请至少选择一个监控品种", color='red')
                return False
            if not self.config.timeframes:
                self.append_log("错误: 请至少选择一个K线周期", color='red')
                return False

            return True
        except ValueError as e:
            self.append_log(f"配置错误: {e}", color='red')
            return False

    def start_monitoring(self, instance):
        """启动监控"""
        if not self.update_config_from_ui():
            return

        self.stop_monitoring = False
        self.is_monitoring = True
        self.start_button.disabled = True
        self.stop_button.disabled = False

        # 禁用输入框和checkbox
        self.price_line_low_input.disabled = True
        self.price_line_high_input.disabled = True
        self.rsi_low_input.disabled = True
        self.rsi_high_input.disabled = True
        self.interval_input.disabled = True
        self.eth_checkbox.disabled = True
        self.btc_checkbox.disabled = True
        self.tf_1m_checkbox.disabled = True
        self.tf_3m_checkbox.disabled = True
        self.tf_5m_checkbox.disabled = True
        self.tf_15m_checkbox.disabled = True
        self.tf_1d_checkbox.disabled = True

        self.append_log("正在启动监控...")
        self.append_log(f"监控品种: {', '.join(self.config.symbols)}")
        self.append_log(f"K线周期: {', '.join(self.config.timeframes)}")
        self.append_log(f"监控条件:")
        self.append_log(f"  价格线 <= {self.config.price_line_low}")
        self.append_log(f"  价格线 >= {self.config.price_line_high}")
        self.append_log(f"  RSI(6) <= {self.config.rsi_low}")
        self.append_log(f"  RSI(6) >= {self.config.rsi_high}")
        self.append_log(f"  检查间隔: {self.config.check_interval}秒")

        # 创建API客户端
        self.api_client = BinanceAPIClient(self.config)

        # 启动监控线程
        self.monitor_thread = threading.Thread(target=self.monitor_loop, daemon=True)
        self.monitor_thread.start()

    def stop_monitoring_action(self, instance):
        """停止监控"""
        self.stop_monitoring = True
        self.is_monitoring = False
        self.start_button.disabled = False
        self.stop_button.disabled = True

        # 启用输入框和checkbox
        self.price_line_low_input.disabled = False
        self.price_line_high_input.disabled = False
        self.rsi_low_input.disabled = False
        self.rsi_high_input.disabled = False
        self.interval_input.disabled = False
        self.eth_checkbox.disabled = False
        self.btc_checkbox.disabled = False
        self.tf_1m_checkbox.disabled = False
        self.tf_3m_checkbox.disabled = False
        self.tf_5m_checkbox.disabled = False
        self.tf_15m_checkbox.disabled = False
        self.tf_1d_checkbox.disabled = False

        self.append_log("监控已停止")

        # 停止语音播报
        if self.tts_manager:
            self.tts_manager.stop()

        if self.api_client:
            self.api_client.close()

    @mainthread
    def append_log(self, text, color=None):
        """添加日志（线程安全）

        Args:
            text: 日志文本
            color: 可选颜色，如'red'、'green'等，None为默认颜色
        """
        current_time = datetime.now().strftime('%H:%M:%S')

        # 根据颜色添加markup标记
        if color == 'red':
            colored_text = f"[color=ff0000]{text}[/color]"
        elif color == 'green':
            colored_text = f"[color=00ff00]{text}[/color]"
        elif color == 'yellow':
            colored_text = f"[color=ffff00]{text}[/color]"
        else:
            colored_text = text

        new_text = f"[{current_time}] {colored_text}"

        # 保留最近100行
        lines = self.log_label.text.split('\n')
        if len(lines) > 100:
            lines = lines[-100:]

        lines.append(new_text)
        self.log_label.text = '\n'.join(lines)

    @mainthread
    def show_alert_notification(self, title, message):
        """显示告警通知"""
        if ANDROID:
            # 安卓通知
            notification.notify(
                title=title,
                message=message,
                app_name='价格监控',
                timeout=10
            )
            # 震动提醒
            try:
                vibrator.vibrate(1)  # 震动1秒
            except:
                pass
        else:
            # 非安卓环境，打印到控制台
            print(f"通知: {title} - {message}")

        # 语音播报告警信息
        if self.tts_manager and self.tts_manager.is_available:
            # 构建简洁的语音消息
            speech_text = f"监控预警。{message}"
            self.tts_manager.speak(speech_text)
            print(f"TTS播报: {speech_text}")

    def monitor_loop(self):
        """监控循环（在后台线程运行）"""
        check_count = 0

        while not self.stop_monitoring:
            check_count += 1

            # 遍历所有选择的品种和周期组合
            for symbol in self.config.symbols:
                for timeframe in self.config.timeframes:
                    if self.stop_monitoring:
                        break

                    try:
                        # 创建计算器
                        calc = PriceLineCalculator(self.api_client, self.config)

                        # 获取数据
                        success, error = calc.fetch_kline_data(symbol, timeframe)
                        if not success:
                            self.append_log(f"[{symbol}/{timeframe}] 错误: {error}", color='yellow')
                            continue

                        # 计算价格线
                        price_line = calc.calculate_price_line()
                        if price_line is None:
                            self.append_log(f"[{symbol}/{timeframe}] 警告: 计算价格线失败", color='yellow')
                            continue

                        # 计算RSI
                        current_rsi = RSICalculator.calculate_rsi(calc.closes, period=6)
                        if current_rsi is None:
                            self.append_log(f"[{symbol}/{timeframe}] 警告: 计算RSI失败", color='yellow')
                            continue

                        current_price = calc.closes[-1]

                        # 检查告警条件
                        alerts = []
                        speech_parts = []  # 用于语音播报的部分

                        if price_line <= self.config.price_line_low:
                            alert_msg = f"价格线低位: {price_line:.2f} <= {self.config.price_line_low}"
                            alerts.append(alert_msg)
                            speech_parts.append(f"价格线低位 {price_line:.1f}")

                        if price_line >= self.config.price_line_high:
                            alert_msg = f"价格线高位: {price_line:.2f} >= {self.config.price_line_high}"
                            alerts.append(alert_msg)
                            speech_parts.append(f"价格线高位 {price_line:.1f}")

                        if current_rsi <= self.config.rsi_low:
                            alert_msg = f"RSI低位: {current_rsi:.2f} <= {self.config.rsi_low}"
                            alerts.append(alert_msg)
                            speech_parts.append(f"RSI低位 {current_rsi:.1f}")

                        if current_rsi >= self.config.rsi_high:
                            alert_msg = f"RSI高位: {current_rsi:.2f} >= {self.config.rsi_high}"
                            alerts.append(alert_msg)
                            speech_parts.append(f"RSI高位 {current_rsi:.1f}")

                        if alerts:
                            self.append_log("=" * 50, color='red')
                            self.append_log(f"!!! [{symbol}/{timeframe}] 预警触发 !!!", color='red')
                            for alert in alerts:
                                self.append_log(f">> {alert}", color='red')
                            self.append_log(f">> 当前价格: {current_price:.2f}", color='red')
                            self.append_log("=" * 50, color='red')

                            # 发送通知和语音播报
                            speech_msg = f"{symbol} {timeframe}周期，" + "、".join(speech_parts)
                            self.show_alert_notification(f"{symbol} 监控预警", speech_msg)
                        else:
                            # 正常状态，显示简略信息
                            status = (f"[{symbol}/{timeframe}] "
                                     f"价格:{current_price:.2f} | "
                                     f"价格线:{price_line:.1f} | "
                                     f"RSI:{current_rsi:.1f}")
                            self.append_log(status)

                    except Exception as e:
                        self.append_log(f"[{symbol}/{timeframe}] 异常: {str(e)}", color='yellow')

                if self.stop_monitoring:
                    break

            # 等待下次检查
            if not self.stop_monitoring:
                time.sleep(self.config.check_interval)


class MonitorApp(App):
    """主应用"""

    def build(self):
        # 注册中文字体（必须在build之前）
        self.setup_chinese_font()

        # 请求安卓权限
        if ANDROID:
            request_permissions([
                Permission.INTERNET,
                Permission.VIBRATE,
                Permission.WAKE_LOCK
            ])

        return MonitorWidget()

    def setup_chinese_font(self):
        """配置中文字体支持"""
        # 获取字体文件路径
        font_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fonts')
        font_path = os.path.join(font_dir, 'NotoSansSC-Regular.otf')

        # 如果字体文件存在，注册字体
        if os.path.exists(font_path):
            LabelBase.register(name='NotoSans', fn_regular=font_path)
            print(f"中文字体加载成功: {font_path}")
        else:
            print(f"警告: 字体文件不存在: {font_path}")
            # 尝试使用系统字体（macOS）
            system_fonts = [
                '/System/Library/Fonts/PingFang.ttc',
                '/System/Library/Fonts/STHeiti Light.ttc',
                '/Library/Fonts/Arial Unicode.ttf'
            ]
            for sys_font in system_fonts:
                if os.path.exists(sys_font):
                    try:
                        LabelBase.register(name='NotoSans', fn_regular=sys_font)
                        print(f"使用系统字体: {sys_font}")
                        break
                    except:
                        continue

    def on_pause(self):
        """应用暂停时保持运行"""
        return True

    def on_resume(self):
        """应用恢复时"""
        pass


if __name__ == '__main__':
    MonitorApp().run()
