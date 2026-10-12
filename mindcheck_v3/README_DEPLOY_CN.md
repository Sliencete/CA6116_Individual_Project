# MindCheck V3.5 — 公共链接课堂测试版

这是基于 MindCheck V3.3 源码整理的云部署版本，重新加入 V3.4 的主要评估校准规则。**原始 V3.4 ZIP 在本次工作环境中不可用，因此此包不是 V3.4 的逐字节复制。** 保留 Teacher / Student 双端、Explain–Apply–Transfer、证据评价、反思和原有界面风格。

## 已经做好

- 固定、可重复使用的 **ReLU Check Code: `RELU-DEMO`**。
- 三道预设问题保存在 `demo_seed.py`，数据库首次启动自动写入；应用重启后也会自动确保该 Code 存在。
- 学生通过公开链接输入 `RELU-DEMO` 即可进入；每个人的页面状态独立，问题一致。
- 继续使用真实 OpenAI API 进行 Explain / Apply / Transfer 语义评价，失败时显示 Unavailable，不伪造 Developing。
- Teacher Setup、题目生成、预览、发布仍可用，但云端教师入口需要私人 `TEACHER_PIN`。
- 默认 SQLite；可配置 `DATABASE_URL` 连接托管 PostgreSQL 以持久保存学生答卷和额外创建的 Checks。
- 评估提示词已重新加入 V3.4 的关键校准规则：Strong 不要求冗长答案、按实际问题判断、支持语义等价、可使用教师参考材料。

## A. 本地测试

在包含 `app.py` 的文件夹中打开 CMD：

```cmd
python -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt
```

在 `app.py` 同级目录创建 `.env`：

```ini
OPENAI_API_KEY=你的API密钥
OPENAI_MODEL=gpt-4.1-mini
TEACHER_PIN=你自己设置的私人PIN
```

**OPENAI_MODEL 可以改成你原来 V3.4 已验证可用的模型名称。**

启动：

```cmd
python -m streamlit run app.py
```

学生端输入 `RELU-DEMO`。教师端需要私人 PIN。

## B. 生成公开链接（Streamlit Community Cloud）

1. 解压本 ZIP。进入 `mindcheck_v3` 文件夹，确保能看到 `app.py`、`requirements.txt`、`demo_seed.py`、`database.py` 等文件。
2. 登录 GitHub，新建一个 Repository（建议命名 `mindcheck-demo`）。上传 **mindcheck_v3 文件夹里的内容** 到 Repository 根目录。不要上传 `.env`、`.venv`、`mindcheck.db`、`secrets.toml` 或任何 API key。
3. 打开 https://share.streamlit.io/ ，使用 GitHub 登录，点击 **Create app**，选择这个 Repository、main 分支和入口文件 `app.py`。
4. 在 **Advanced settings / Secrets**（或部署后的 App settings → Secrets）填入：

```toml
OPENAI_API_KEY = "你的真实API密钥"
OPENAI_MODEL = "gpt-4.1-mini"
TEACHER_PIN = "你自己设置的私人PIN"
```

5. 点击 Deploy。成功后你会得到一个 `https://...streamlit.app` 的公开链接。
6. 在另一台设备/无痕窗口打开链接，输入 `RELU-DEMO`，完整走完 Explain → Apply → Transfer → Profile → Reflection。**不要只测试自己电脑的 localhost。**
7. 课堂上展示这个链接（可另生成 QR code）和 `RELU-DEMO`，不需要现场创建题目。

可在公开链接后加 `?code=RELU-DEMO`，进入 Join Check 时自动填入演示码。

## C. 数据保存非常重要

默认 SQLite 在 Community Cloud 上是**临时存储**。应用重启、重新部署或容器更换后，临时答卷和额外生成的 Check Code **可能丢失**；不过预设 `RELU-DEMO` 会自动重建。

如果你要在课后稳定保留所有同学的答案，必须配置**托管 PostgreSQL**：

1. 自行创建一个可从云端访问的 PostgreSQL 数据库（例如 Neon 或 Supabase 提供的 PostgreSQL）。
2. 从数据库提供方复制连接串，放到 Streamlit Cloud Secrets：

```toml
DATABASE_URL = "postgresql://USER:PASSWORD@HOST/DATABASE?sslmode=require"
```

3. 重启应用。系统会自动建表、写入 `RELU-DEMO`，后续回答写入数据库。
4. 注意不要把数据库连接串放进 GitHub。

数据库配置是**可选**的：短时课堂演示不要求 PostgreSQL，但需要接受临时答卷可能丢失。不能把默认 SQLite 当作持久化云数据库。

## D. 答辩前检查清单

- [ ] 公共链接在另一台设备上能打开，不要求登录。
- [ ] 输入 `RELU-DEMO`，看到 ReLU 主题和固定三道题。
- [ ] AI connection 显示 Connected；如失败，检查 Cloud Secrets、API 余额和模型名称。
- [ ] 提交三道答案，能得到 Strong / Developing / Limited 证据级别，而不是 Unavailable。
- [ ] Reflection 能正常完成。
- [ ] 教师 PIN 不公开给同学。
- [ ] 控制 API 额度和课堂测试人数；公开应用可能产生 API 调用费用。
- [ ] 不收集真实姓名、学号或敏感信息；使用 nickname 即可。

## E. 注意

- 这是公开链接课堂**试用**版本，不是已通过学校隐私/安全审批的正式部署系统。
- 只需同学访问学生端，教师端已加 PIN 防止匿名用户随意生成新题消耗 API。
- API 费用由你的 OpenAI API 账户承担；ChatGPT Plus 不包含 API 额度。
- 目前无法代你登录 GitHub、Streamlit Cloud、数据库提供商，也不能在未部署的情况下提供真实公网网址。
