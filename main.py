from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import httpx
from openai import OpenAI
import os
import io
import PyPDF2

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# 连接 DeepSeek 大脑
client = OpenAI(
    api_key=os.environ.get("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com",
    http_client=httpx.Client(timeout=90.0)
)

@app.get("/", response_class=HTMLResponse)
async def read_root():
    with open("index.html", "r", encoding="utf-8") as f:
        return f.read()

# ================= 模块1：简历诊断 =================
@app.post("/api/match")
async def match_resume(jd: str = Form(...), mode: str = Form(...), file: UploadFile = File(...)):
    content = await file.read()
    pdf_reader = PyPDF2.PdfReader(io.BytesIO(content))
    resume_text = "".join([page.extract_text() + "\n" for page in pdf_reader.pages])

    mode_prompt = "侧重潜力、学习能力、实习经历。" if mode == "campus" else "侧重业务落地能力、项目深度。"
    system_prompt = f"你是资深HR。分析JD和简历匹配度（0-100分），指出缺失项，用STAR法则重写一段经历。当前模式：{mode_prompt}"
    user_content = f"【JD】:\n{jd}\n\n【简历】:\n{resume_text}"
    
    res = client.chat.completions.create(model="deepseek-chat", messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_content}])
    
    return {"result": res.choices[0].message.content, "original_text": resume_text}

class HtmlResumeRequest(BaseModel):
    jd: str
    original_text: str
    diagnosis_text: str
    target_lang: str = "中文"

# ================= 模块2：生成网页简历 =================
@app.post("/api/gen_html_resume")
async def gen_html_resume(req: HtmlResumeRequest):
    # 注意这里：为了避免 Python 报错，我把 CSS 的大括号换成了小括号，AI 能看懂的
    system_prompt = f"""
    你是一位顶尖的前端设计师。请根据JD、【原始简历文本】和【HR诊断建议】，重写一份极具竞争力的简历，直接输出完整的HTML代码。
    
    【极其严格的要求，违反将导致代码崩溃】：
    1. 绝对不要输出任何解释性的话（如“以下是为您生成的代码”），你的回答必须直接以 `<!DOCTYPE html>` 开头！
    2. 使用内联CSS(放在<style>里)，风格要求现代高级（主色调深蓝灰白）。
    3. 【核心要求】必须在 `<style>` 里面加上这段打印分页魔法，确保简历很长时也不会被切断：
       @media print (
           body ( -webkit-print-color-adjust: exact; )
           .page-break ( page-break-before: always; )
       )
    4. 请务必从【原始简历文本】中提取真实的姓名、电话、邮箱、学校等基本信息，绝对不要自己编造！
    5. 请将简历的所有内容翻译并输出为【{req.target_lang}】。
    """
    user_content = f"【JD】:\n{req.jd}\n\n【原始简历文本】:\n{req.original_text}\n\n【HR诊断建议】:\n{req.diagnosis_text}"
    
    res = client.chat.completions.create(model="deepseek-chat", messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_content}], temperature=0.7)
    return {"html": res.choices[0].message.content.replace("```html", "").replace("```", "").strip()}

# ================= 模块3：HR 沟通外挂 =================
class ReplyRequest(BaseModel):
    jd: str
    hr_message: str
    mode: str

@app.post("/api/hr_reply")
async def gen_hr_reply(req: ReplyRequest):
    mode_style = "谦虚好学、充满热情。" if req.mode == "campus" else "专业、直接、不卑不亢。"
    system_prompt = f"你是职场沟通专家。HR发来了一句话，请结合JD代写回复。要求：{mode_style} 语气自然，150字以内。"
    user_content = f"【JD】:\n{req.jd}\n\n【HR的话】:\n{req.hr_message}"
    res = client.chat.completions.create(model="deepseek-chat", messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_content}])
    return {"result": res.choices[0].message.content}

# ================= 模块4：AI 模拟面试 =================
class InterviewRequest(BaseModel):
    jd: str
    history: list
    is_end: bool = False

@app.post("/api/interview")
async def mock_interview(req: InterviewRequest):
    if req.is_end:
        system_prompt = "你是一位面试官。请根据之前的面试记录，给候选人生成一份终期评估报告（包含打分、优缺点、建议）。"
    else:
        system_prompt = f"你是一位专业面试官，岗位JD：{req.jd}。请根据回答进行追问或点评，每次只问一个问题，简短直接。"
    
    messages = [{"role": "system", "content": system_prompt}] + req.history
    if req.is_end:
        messages.append({"role": "user", "content": "面试结束，请给我评估报告。"})
        
    res = client.chat.completions.create(model="deepseek-chat", messages=messages)
    return {"reply": res.choices[0].message.content}

# ================= 模块5：岗位推荐 =================
class MajorRequest(BaseModel):
    major: str
    mode: str

@app.post("/api/recommend_jobs")
async def recommend_jobs(req: MajorRequest):
    system_prompt = f"你是职业规划专家。根据用户的专业，推荐5个最适合的岗位，并给出每个岗位的匹配理由和未来发展方向。当前模式：{'校招' if req.mode == 'campus' else '社招'}。请用清晰的列表输出。"
    user_content = f"我的专业是：{req.major}"
    res = client.chat.completions.create(model="deepseek-chat", messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_content}])
    return {"result": res.choices[0].message.content}