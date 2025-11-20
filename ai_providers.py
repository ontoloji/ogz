"""
Multi-AI Question Tool - AI Provider Entegrasyonları
Desteklenen AI'lar: OpenAI, Anthropic Claude, Google Gemini
"""

import logging
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
import time


class AIProvider(ABC):
    """AI Provider abstract sınıfı"""

    def __init__(self, api_key: str, model: str = None):
        self.api_key = api_key
        self.model = model
        self.logger = logging.getLogger(self.__class__.__name__)

    @abstractmethod
    def ask_question(self, question: str, **kwargs) -> str:
        """Soruyu AI'ya sor ve cevabı döndür"""
        pass

    @abstractmethod
    def get_provider_name(self) -> str:
        """Provider ismini döndür"""
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Provider kullanılabilir mi?"""
        pass


class OpenAIProvider(AIProvider):
    """OpenAI GPT Provider"""

    def __init__(self, api_key: str, model: str = "gpt-4"):
        super().__init__(api_key, model)
        self.available = False

        try:
            import openai
            self.openai = openai
            self.client = openai.OpenAI(api_key=api_key)
            self.available = True
        except ImportError:
            self.logger.error("openai paketi yüklü değil. 'pip install openai' çalıştırın")
        except Exception as e:
            self.logger.error(f"OpenAI başlatma hatası: {e}")

    def ask_question(self, question: str, **kwargs) -> str:
        """OpenAI'ya soru sor"""
        if not self.available:
            return "❌ HATA: OpenAI kütüphanesi yüklü değil"

        try:
            max_tokens = kwargs.get('max_tokens', 2000)
            temperature = kwargs.get('temperature', 0.7)

            self.logger.info(f"OpenAI'ya soru soruluyor (model: {self.model})...")

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "user", "content": question}
                ],
                max_tokens=max_tokens,
                temperature=temperature
            )

            answer = response.choices[0].message.content
            self.logger.info("OpenAI cevabı alındı")
            return answer

        except Exception as e:
            error_msg = f"❌ HATA: {str(e)}"
            self.logger.error(f"OpenAI API hatası: {e}")
            return error_msg

    def get_provider_name(self) -> str:
        return f"OpenAI ({self.model})"

    def is_available(self) -> bool:
        return self.available and bool(self.api_key)


class AnthropicProvider(AIProvider):
    """Anthropic Claude Provider"""

    def __init__(self, api_key: str, model: str = "claude-3-5-sonnet-20241022"):
        super().__init__(api_key, model)
        self.available = False

        try:
            import anthropic
            self.anthropic = anthropic
            self.client = anthropic.Anthropic(api_key=api_key)
            self.available = True
        except ImportError:
            self.logger.error("anthropic paketi yüklü değil. 'pip install anthropic' çalıştırın")
        except Exception as e:
            self.logger.error(f"Anthropic başlatma hatası: {e}")

    def ask_question(self, question: str, **kwargs) -> str:
        """Claude'a soru sor"""
        if not self.available:
            return "❌ HATA: Anthropic kütüphanesi yüklü değil"

        try:
            max_tokens = kwargs.get('max_tokens', 2000)
            temperature = kwargs.get('temperature', 0.7)

            self.logger.info(f"Claude'a soru soruluyor (model: {self.model})...")

            response = self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                temperature=temperature,
                messages=[
                    {"role": "user", "content": question}
                ]
            )

            answer = response.content[0].text
            self.logger.info("Claude cevabı alındı")
            return answer

        except Exception as e:
            error_msg = f"❌ HATA: {str(e)}"
            self.logger.error(f"Anthropic API hatası: {e}")
            return error_msg

    def get_provider_name(self) -> str:
        return f"Anthropic Claude ({self.model})"

    def is_available(self) -> bool:
        return self.available and bool(self.api_key)


class GoogleGeminiProvider(AIProvider):
    """Google Gemini Provider"""

    def __init__(self, api_key: str, model: str = "gemini-pro"):
        super().__init__(api_key, model)
        self.available = False

        try:
            import google.generativeai as genai
            self.genai = genai
            genai.configure(api_key=api_key)
            self.client = genai.GenerativeModel(model)
            self.available = True
        except ImportError:
            self.logger.error("google-generativeai paketi yüklü değil. 'pip install google-generativeai' çalıştırın")
        except Exception as e:
            self.logger.error(f"Google Gemini başlatma hatası: {e}")

    def ask_question(self, question: str, **kwargs) -> str:
        """Gemini'ye soru sor"""
        if not self.available:
            return "❌ HATA: Google Generative AI kütüphanesi yüklü değil"

        try:
            self.logger.info(f"Gemini'ye soru soruluyor (model: {self.model})...")

            response = self.client.generate_content(question)

            answer = response.text
            self.logger.info("Gemini cevabı alındı")
            return answer

        except Exception as e:
            error_msg = f"❌ HATA: {str(e)}"
            self.logger.error(f"Google Gemini API hatası: {e}")
            return error_msg

    def get_provider_name(self) -> str:
        return f"Google Gemini ({self.model})"

    def is_available(self) -> bool:
        return self.available and bool(self.api_key)


class CohereProvider(AIProvider):
    """Cohere Provider (Opsiyonel)"""

    def __init__(self, api_key: str, model: str = "command"):
        super().__init__(api_key, model)
        self.available = False

        try:
            import cohere
            self.cohere = cohere
            self.client = cohere.Client(api_key)
            self.available = True
        except ImportError:
            self.logger.error("cohere paketi yüklü değil. 'pip install cohere' çalıştırın")
        except Exception as e:
            self.logger.error(f"Cohere başlatma hatası: {e}")

    def ask_question(self, question: str, **kwargs) -> str:
        """Cohere'ye soru sor"""
        if not self.available:
            return "❌ HATA: Cohere kütüphanesi yüklü değil"

        try:
            max_tokens = kwargs.get('max_tokens', 2000)
            temperature = kwargs.get('temperature', 0.7)

            self.logger.info(f"Cohere'ye soru soruluyor (model: {self.model})...")

            response = self.client.generate(
                model=self.model,
                prompt=question,
                max_tokens=max_tokens,
                temperature=temperature
            )

            answer = response.generations[0].text
            self.logger.info("Cohere cevabı alındı")
            return answer

        except Exception as e:
            error_msg = f"❌ HATA: {str(e)}"
            self.logger.error(f"Cohere API hatası: {e}")
            return error_msg

    def get_provider_name(self) -> str:
        return f"Cohere ({self.model})"

    def is_available(self) -> bool:
        return self.available and bool(self.api_key)


class AIProviderManager:
    """AI Provider yöneticisi"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.providers: Dict[str, AIProvider] = {}
        self.logger = logging.getLogger(__name__)

        self._initialize_providers()

    def _initialize_providers(self):
        """Provider'ları başlat"""
        # OpenAI
        if self.config.get('openai', {}).get('enabled', False):
            api_key = self.config['openai'].get('api_key', '')
            model = self.config['openai'].get('model', 'gpt-4')
            self.providers['openai'] = OpenAIProvider(api_key, model)

        # Anthropic Claude
        if self.config.get('anthropic', {}).get('enabled', False):
            api_key = self.config['anthropic'].get('api_key', '')
            model = self.config['anthropic'].get('model', 'claude-3-5-sonnet-20241022')
            self.providers['anthropic'] = AnthropicProvider(api_key, model)

        # Google Gemini
        if self.config.get('google', {}).get('enabled', False):
            api_key = self.config['google'].get('api_key', '')
            model = self.config['google'].get('model', 'gemini-pro')
            self.providers['google'] = GoogleGeminiProvider(api_key, model)

        # Cohere (Opsiyonel)
        if self.config.get('cohere', {}).get('enabled', False):
            api_key = self.config['cohere'].get('api_key', '')
            model = self.config['cohere'].get('model', 'command')
            self.providers['cohere'] = CohereProvider(api_key, model)

    def get_available_providers(self) -> Dict[str, AIProvider]:
        """Kullanılabilir provider'ları döndür"""
        return {
            name: provider
            for name, provider in self.providers.items()
            if provider.is_available()
        }

    def ask_all(self, question: str, selected_providers: list = None, **kwargs) -> Dict[str, str]:
        """Seçili tüm provider'lara soru sor"""
        results = {}

        if selected_providers is None:
            selected_providers = list(self.providers.keys())

        for name in selected_providers:
            if name in self.providers:
                provider = self.providers[name]
                if provider.is_available():
                    try:
                        answer = provider.ask_question(question, **kwargs)
                        results[provider.get_provider_name()] = answer
                    except Exception as e:
                        self.logger.error(f"{name} hatası: {e}")
                        results[provider.get_provider_name()] = f"❌ HATA: {str(e)}"
                else:
                    results[name] = "❌ Provider kullanılamıyor (API key eksik veya kütüphane yüklü değil)"

        return results
