import openai
import json
import re
from kiwipiepy import Kiwi
from config import OPENAI_API_KEY

client = openai.OpenAI(api_key=OPENAI_API_KEY)

# Kiwi 초기화
kiwi = Kiwi()


def clean_text(text):
    """불필요한 공백 및 줄바꿈을 제거"""
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def detect_filler_words(text):
    """발음 실수 감지 (불필요한 필러 단어)"""
    filler_patterns = [
        r"\b어+\.{0,2}\b",  # "어.."
        r"\b음+\.{0,2}\b",  # "음.."
        r"\b그+\.{0,2}\b",  # "그.."
        r"\b저기+\.{0,2}\b",  # "저기.."
        r"\.{3,}",  # "..."
    ]

    matches = []
    for pattern in filler_patterns:
        found = re.findall(pattern, text)
        if found:
            matches.extend(found)

    return matches if matches else None

def analyze_text_with_gpt(text, question, job_role):
    """GPT를 이용하여 면접관의 입장에서 문법적 오류, 전문성 부족, 발음 실수를 분석하고 JSON 데이터로 변환"""
    prompt = f"""
    당신은 {job_role} 직무 면접을 진행하는 면접관입니다.  
    아래는 면접 질문과 지원자의 답변입니다. 면접관의 입장에서 답변을 평가하고, **각 문제 부분을 하나의 문제 유형에만 할당하여** 피드백을 제공합니다.  
    답변은 음성을 텍스트화한 것입니다. 그 점을 고려하여 답변해주세요.  

    **면접 질문:** {question}  
    **지원자의 답변:**  
    "{text}"  

    답변을 평가할 때 다음 기준을 고려하세요:  
    - **문법적 오류**: 맞춤법, 문장 구조 및 문장이 자연스럽지 않은 부분.  
    - **전문성 부족**: 너무 캐주얼한 표현, 직무와 관련 없는 내용, 애매한 답변, 반말 답변.  
    - **발음 실수 및 전달력**: 상식적으로 읽히지 않는 부분 또는 이상하게 반복되는 부분 ("이이이이이") 또는 끝맺음이 없는 부분.  
    - **필러 단어**: 불필요한 필러 단어 ("음..", "어..", "...") 사용 여부.  
    - **질문과 불일치**: 답변이 면접 질문과 맞지 않거나 질문에 대한 직접적인 응답이 아닌 경우.  

    **반드시 지켜야 할 원칙:**  
    1. **각 오류는 하나의 문제 유형에만 할당해야 합니다.** 같은 문장에서 여러 문제 유형이 발견되면, 해당 부분을 **나눠** 각각의 문제로 분석하세요. 문제 없는 부분을 문제 있는 부분이랑 같이 언급하지 마세요.  
    2. **불필요한 필러 단어 문제는 한 번만 언급하세요.** 만약 필러 단어가 여러 곳에서 발견되더라도, 피드백은 단 한 번만 제공하세요. 
    3. **딱 필러 단어만 문제 있는 특정 단어 부분으로 지정하세요.**  
    4. **문제가 없는 경우 출력하지 마세요.** 문제 있는 부분만 출력해야 하며, `"문제 없음"`과 같은 응답을 포함하지 마세요.  
    5. **문제 유형이 필러 단어가 아닐 경우, 문제 있는 부분에 필러 단어가 포함되지 않아야 합니다.**  
    6. **질문과 불일치 유형이 있는 경우, 그 이유를 명확하게 설명하세요.**  
    
    **JSON 형식으로만 응답하세요. 다른 설명은 하지 마세요.**  
    JSON 데이터는 반드시 **아래 형식**을 따라야 합니다:  
    ```json
    {{
      "analysis": [
        {{
          "error_text": "문제 있는 부분",
          "error_type": "문법 오류 / 전문성 부족 / 발음 실수 / 질문과 불일치 / 필러 단어 중 하나",
          "feedback": "이 부분이 왜 문제가 되는지 설명",
          "suggestion": "더 나은 표현 제안"
        }}
      ]
    }}
    ```
    **반드시 JSON 형식만 출력하세요. 추가 설명을 포함하지 마세요.**
    """

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "system", "content": "당신은 경험이 풍부한 면접관입니다. 지원자의 답변을 분석하고, 면접자의 입장에서 구체적인 피드백을 제공합니다."},
                  {"role": "user", "content": prompt}]
    )

    full_response = response.choices[0].message.content.strip()

    json_match = re.search(r'\{[\s\S]*\}', full_response)

    if json_match:
        json_text = json_match.group(0)
        try:
            json_response = json.loads(json_text)
        except json.JSONDecodeError:
            json_response = {"error": "GPT가 유효한 JSON을 생성하지 않았습니다.", "raw_output": full_response}
    else:
        json_response = {"error": "GPT 응답에서 JSON 데이터를 찾을 수 없습니다.", "raw_output": full_response}

    return full_response, json_response


def generate_follow_up(answer, question, job_role):
    cleaned_answer = clean_text(answer)

    prompt = f"""
    지원 직무: {job_role}
    면접 질문: {question}
    지원자의 답변: {cleaned_answer}

    - 지원자의 답변을 기반으로, 더 깊이 있는 기술적 질문을 생성하세요.
    - 후속 질문은 반드시 직무 관련 기술, 원리, 또는 실무 경험과 관련된 것이어야 합니다.
    - 지원자가 언급한 경험에 대해 구체적인 후속 질문을 만드세요.
    - 단순한 추가 설명 요청이 아니라, 실무에서 어떻게 적용하는지 또는 깊이 있는 지식을 확인하는 질문이어야 합니다.
    - 3개의 질문을 생성하세요.
    - JSON 형식으로 제공해주세요.

    JSON 출력 예시:
    {{
        "후속 질문 리스트": [
            "API 응답 속도 최적화 시, 쿼리 최적화 외에도 고려할 수 있는 다른 방법이 있나요?",
            "SQL 쿼리를 최적화할 때 가장 중요한 기준은 무엇인가요?",
            "코드 리팩토링 시, 유지보수성을 높이기 위해 가장 중요한 원칙은 무엇인가요?"
        ]
    }}
    """

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "system", "content": "당신은 기술 면접 질문을 잘 만드는 전문가입니다."},
                  {"role": "user", "content": prompt}]
    )

    try:
        follow_up = json.loads(response.choices[0].message.content)
    except json.JSONDecodeError:
        follow_up = {"후속 질문 리스트": ["API 속도 최적화를 할 때 다른 방법도 고려해 보셨나요?"]}

    # 최대 3개 질문만 유지
    follow_up["후속 질문 리스트"] = follow_up["후속 질문 리스트"][:3]

    return follow_up


def analyze_answer(question, answer, job_role):
    """면접 답변을 종합적으로 분석하여 반환"""
    cleaned_answer = clean_text(answer)
    filler_issues = detect_filler_words(cleaned_answer)
    analysis_result = analyze_text_with_gpt(cleaned_answer, question, job_role)
    follow_up_question = generate_follow_up(cleaned_answer, question, job_role)

    final_result = {
        "원본 답변": answer,
        "정리된 답변": cleaned_answer,
        "분석 결과": analysis_result,
        "후속 질문": follow_up_question
    }

    return final_result

if __name__ == "__main__":
    # 예제 실행
    question = "자신의 강점은 무엇인가요?"
    answer = """
    어.. 제 강점은.. 음.. 새로운 환경에서도 빠르게 적응하고 개발 실력을 키워나가는 거예요. 원래는 다른 전공이었는데.. 개발이 너무 재밌어 보여서.. 어.. 독학하면서 포트폴리오도 만들고, 결국 전과까지 하게 됐어요.

어.. 예를 들면, 처음에 웹 개발을 배울 때.. 진짜 아무것도 몰라서 헤맸는데.. 어.. 직접 토이 프로젝트 만들어 보고.. 어.. 삽질도 많이 하면서.. 결국 풀스택 개발까지 할 수 있게 됐어요. 어.. 특히 전에 백엔드에서 API 속도가 너무 느려지는 문제가 있어서.. 어.. 그냥 두지 않고 직접 로그 찍어가면서 원인을 찾아봤어요. 어.. 결국 DB 쿼리 최적화해서 응답 속도를 40% 줄였죠.

그리고 저는.. 코드 그냥 되는 대로 짜는 게 아니라, 좀 더 깔끔하고 유지보수하기 좋게 만드는 걸 좋아해요. 어.. 기능만 되면 끝! 이게 아니라, 리팩토링도 자주 하고.. 음.. 다른 사람이 봐도 이해하기 쉽게 만들려고 신경 씁니다.

그래서 결론적으로, 새로운 걸 배우는 데 주저하지 않는 거랑.. 어.. 개발 실력을 빠르게 키워서 실무에 적응할 수 있는 게 제 강점이라고 생각합니다.
    """
    job_role = "소프트웨어 개발자"

    analysis = analyze_answer(question, answer, job_role)
    print("\n📌 최종 분석 결과:\n")
    print(json.dumps(analysis, indent=4, ensure_ascii=False))
