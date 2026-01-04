import os
from dotenv import load_dotenv
from hello_agents import HelloAgentsLLM, SimpleAgent

# 加载环境变量
load_dotenv()

def test_translator():
    print("🚀 开始测试 UnsplashTranslator...")
    try:
        llm = HelloAgentsLLM()
        translator = SimpleAgent(
            name="UnsplashTranslator",
            llm=llm,
            system_prompt="You are a professional translator. Translate travel attraction or city names to English for image searching. Return ONLY the English translation, no other text."
        )
        
        test_cases = ["天安门广场", "故宫博物院", "北京"]
        for text in test_cases:
            print(f"输入: {text}")
            response = translator.run(f"Translate to English: {text}")
            print(f"输出: {response.strip()}")
            
        print("✅ 测试完成！")
    except Exception as e:
        print(f"❌ 测试失败: {e}")

if __name__ == "__main__":
    test_translator()
