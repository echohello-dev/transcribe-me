import os
import unittest
from unittest.mock import patch, Mock
from transcribe_me.summarization import summarizer

class TestSummarization(unittest.TestCase):
    @patch('openai.chat.completions.create')
    def test_generate_summary_openai(self, mock_completion):
        mock_completion.return_value.choices = [Mock(message=Mock(content='This is a summary'))]
        model_config = {
            'temperature': 0.1,
            'max_tokens': 2048,
            'model': 'gpt-4',
            'system_prompt': 'Generate a summary'
        }
        result = summarizer.generate_summary('This is a transcription.', 'openai', model_config)
        self.assertEqual(result, 'This is a summary')

    @patch('anthropic.Anthropic')
    def test_generate_summary_anthropic(self, mock_anthropic):
        mock_client = mock_anthropic.return_value
        mock_client.messages.create.return_value.content = [Mock(text='This is a summary')]
        model_config = {
            'temperature': 0.1,
            'max_tokens': 2048,
            'model': 'claude-3-sonnet-20240229',
            'system_prompt': 'Generate a summary'
        }
        result = summarizer.generate_summary('This is a transcription.', 'anthropic', model_config)
        self.assertEqual(result, 'This is a summary')

if __name__ == '__main__':
    unittest.main()