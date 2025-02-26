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
    """부족한 답변을 보완하기 위한 후속 질문 생성 (최대 3개 제한)"""
    prompt = f"""
    지원 직무: {job_role}
    면접 질문: {question}
    지원자의 답변: {answer}

    - 위의 답변에서 부족한 점을 보완할 수 있도록 후속 질문을 생성해주세요.
    - 최대 3개의 질문만 생성하세요.
    - JSON 형식으로 제공해주세요.
    JSON 키: "후속 질문 리스트"
    예시:
    {{
        "후속 질문 리스트": ["추가 질문 1", "추가 질문 2", "추가 질문 3"]
    }}
    """

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "system", "content": "당신은 면접 질문을 잘 만드는 전문가입니다."},
                  {"role": "user", "content": prompt}]
    )

    try:
        follow_up = json.loads(response.choices[0].message.content)
    except json.JSONDecodeError:
        follow_up = {"후속 질문 리스트": ["조금 더 자세히 설명해 주실 수 있나요?"]}

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
        "발음 실수": filler_issues if filler_issues else "없음",
        "분석 결과": analysis_result,
        "후속 질문": follow_up_question
    }

    return final_result

if __name__ == "__main__":
    # 예제 실행
    question = "자신의 강점은 무엇인가요?"
    answer = "안녕하세요, 지원자 홍길동입니다. 싱이ㅣ압ㄹ 어.. 제 강점은.. 음.. 문제 해결 능력이 뛰어나다는 점입니다. 어.. 그러니까.. 예를 들면, 이전 병신 회사에서.. 어.. 팀 프로젝트 중에.. 어.. 예상치 못한.. 어.. 기술적인 문제가 발생했을 때.. 음.. 그냥 다른 사람이 해결해 주기를 기다리는 게 아니라.. 오리는 날아서 훨훨 날아갔어요. 음.. 직접 자료를 찾아보고.. 어.. 해결 방법을 모색해서.. 어.. 문제를 해결했던 경험이 있습니다. 어.. 그리고.. 음.. 저는 팀워크도 시발 중요하게 생각하는데.. 음.. 혼자만의 노력보다 협업을 통해 더 나은 해결책을 찾으려고 합니다. 음.. 그래서 저는.. 어.. 문제 해결 능력과 협업 능력이 강점이라고."
    job_role = "소프트웨어 개발자"

    analysis = analyze_answer(question, answer, job_role)
    print("\n📌 최종 분석 결과:\n")
    print(json.dumps(analysis, indent=4, ensure_ascii=False))
