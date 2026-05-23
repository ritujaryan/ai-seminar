import requests
import json
import time

BASE_URL = "http://localhost:8000/api/v1"

def load_ai_seminar():
    print("=" * 80)
    print("  LOADING SEMINAR: 'AI - Where to Begin'")
    print("  Presenter: Rahul Mehta, Principal AI Tech Lead @ Google DeepMind")
    print("  Audience: 2nd-4th Year Engineering Students")
    print("=" * 80)

    # ─── SLIDE DECK ──────────────────────────────────────────────────────
    ai_deck = {
        "title": "AI — Where to Begin: A Practical Roadmap for Engineering Students",
        "slides": [
            # ── SLIDE 0 ──────────────────────────────────────────────────
            {
                "slide_id": 0,
                "title": "Welcome & Why AI Matters Right Now",
                "content": (
                    "Good morning everyone, thank you for being here on a Saturday. "
                    "My name is Rahul Mehta, I have been working in the AI space for about twelve years now — "
                    "started with classical machine learning at a startup, moved to deep learning research at Microsoft, "
                    "and currently lead a team at Google DeepMind that works on large language models. "
                    "So why should you care about AI as an engineering student in 2026? "
                    "Let me give you three concrete reasons. "
                    "First, AI is no longer a niche research topic — it is embedded in almost every product you use daily: "
                    "Google Search, Instagram recommendations, UPI fraud detection, even the autocorrect on your phone. "
                    "Second, the job market has fundamentally shifted. Five years ago, companies hired separate ML teams. "
                    "Today, every software engineer is expected to understand at least the basics of how models work, "
                    "how to call an API, how to evaluate outputs, and when NOT to use AI. "
                    "Third — and this is personal — AI gives you leverage. A single engineer with the right AI tools "
                    "can build products that would have taken a team of twenty people just three years ago. "
                    "That is an insane amount of individual power, and I want you to have it. "
                    "Today's session is structured as a roadmap. We will go from the very basics — what AI actually is — "
                    "all the way to practical advice on building your first projects and getting hired. "
                    "I will be pausing for questions after every major section, so please do not hesitate to interrupt."
                ),
                "notes": "Opening slide. Set the tone — energetic, relatable, no jargon yet. Establish credibility quickly but stay approachable. Make students feel this is for THEM, not a PhD audience.",
                "wait_for_doubts": False
            },
            # ── SLIDE 1 ──────────────────────────────────────────────────
            {
                "slide_id": 1,
                "title": "What Exactly Is AI? Cutting Through the Hype",
                "content": (
                    "Alright, let us start with the most basic question — what IS Artificial Intelligence? "
                    "And I want to be honest with you: the term is massively overhyped and misused. "
                    "At its core, AI is just software that can perform tasks that traditionally required human intelligence. "
                    "That includes recognizing faces in photos, translating languages, playing chess, or generating text. "
                    "Now, there is a hierarchy here that you need to understand. "
                    "At the top, you have AI — the broadest umbrella. Under that sits Machine Learning, which is a subset of AI "
                    "where systems learn patterns from data instead of being explicitly programmed with rules. "
                    "Under Machine Learning, you have Deep Learning — which uses neural networks with many layers "
                    "to automatically extract features from raw data like images, audio, or text. "
                    "And then you have Generative AI — the thing everyone is talking about — which is a subset of Deep Learning "
                    "focused on creating NEW content: text, images, code, music. "
                    "So when your friend says 'I used AI to write my assignment', they specifically used a Generative AI model, "
                    "which is a type of Deep Learning model, which is a type of Machine Learning, which falls under AI. "
                    "Now here is what most people get wrong — they think AI means AGI, Artificial General Intelligence, "
                    "a system that can do EVERYTHING a human can do. We are nowhere close to that. "
                    "What we have today is called Narrow AI — systems that are incredibly good at ONE specific task. "
                    "GPT-4 can write essays but cannot tie your shoelaces. AlphaFold can predict protein structures "
                    "but cannot book a flight. Keep this distinction in mind — it will save you from a lot of confusion."
                ),
                "notes": "Critical foundational slide. Draw the AI > ML > DL > GenAI hierarchy on the whiteboard. Use relatable examples for each layer. Pause for questions — students usually have many here.",
                "wait_for_doubts": True
            },
            # ── SLIDE 2 ──────────────────────────────────────────────────
            {
                "slide_id": 2,
                "title": "The Mathematics You Actually Need",
                "content": (
                    "Now, the question I get asked the most by students is — 'How much math do I really need?' "
                    "And I will give you the honest answer: it depends on what you want to do. "
                    "If you want to USE AI — call APIs, fine-tune models, build applications — you need surprisingly little math. "
                    "Basic intuition is enough. But if you want to BUILD AI — design new architectures, "
                    "publish research papers, work at a lab like DeepMind — you need solid mathematical foundations. "
                    "Let me break down the four pillars. "
                    "First: Linear Algebra. This is non-negotiable. Neural networks are essentially matrix multiplication machines. "
                    "When you hear 'weights', 'embeddings', 'transformations' — that is all linear algebra. "
                    "You need to be comfortable with vectors, matrices, dot products, eigenvalues, and matrix decomposition. "
                    "If you remember one thing: a neural network forward pass is literally input vector times weight matrix plus bias, "
                    "passed through a non-linear function. That is it. "
                    "Second: Calculus. Specifically, multivariable calculus. The entire training process of a neural network "
                    "is based on gradient descent — you compute the derivative of a loss function with respect to each weight, "
                    "and nudge the weights in the direction that reduces the error. Chain rule is your best friend here. "
                    "Third: Probability and Statistics. Every ML model is making probabilistic predictions. "
                    "You need to understand distributions, Bayes theorem, maximum likelihood estimation, "
                    "and hypothesis testing. When a model says 'I am 92 percent confident this is a cat', "
                    "probability theory is what gives that number meaning. "
                    "Fourth: Optimization. Gradient descent, stochastic gradient descent, Adam optimizer — "
                    "these are the algorithms that actually make learning happen. "
                    "Understanding convex vs non-convex optimization helps you debug why your model is not converging. "
                    "Now, the practical advice: do NOT try to master all of this before starting ML. "
                    "Learn just enough to understand what is happening, start building, and then go deeper as needed. "
                    "I will share a specific study plan at the end."
                ),
                "notes": "Students are usually anxious about math. Be reassuring but honest. Emphasize the 'learn as you go' approach. Draw the gradient descent diagram — a ball rolling down a hill to find the minimum.",
                "wait_for_doubts": True
            },
            # ── SLIDE 3 ──────────────────────────────────────────────────
            {
                "slide_id": 3,
                "title": "Python & Essential Tools — Your AI Development Environment",
                "content": (
                    "Let us talk about tools. The first and most important decision has already been made for you — "
                    "the language of AI is Python. Period. "
                    "Yes, there are ML libraries in Julia, Rust, and C++, but 95 percent of tutorials, research code, "
                    "and production ML pipelines are written in Python. Do not fight this. Learn Python well. "
                    "Now, when I say 'learn Python', I do not mean just the syntax. You need to be comfortable with: "
                    "list comprehensions, generators, decorators, context managers, and especially — "
                    "object-oriented programming. Most ML frameworks are heavily class-based. "
                    "Next, your core libraries. NumPy is the foundation — it gives you fast array operations. "
                    "Every single ML library is built on top of NumPy arrays. "
                    "Pandas is for data manipulation — loading CSVs, cleaning data, feature engineering. "
                    "You will spend 60 to 70 percent of any real ML project just cleaning data, and Pandas makes that bearable. "
                    "Matplotlib and Seaborn are for visualization. You MUST be able to plot your data before modeling. "
                    "I cannot stress this enough — if you cannot visualize it, you do not understand it. "
                    "For ML specifically, Scikit-learn is your starting point. It has every classical ML algorithm — "
                    "linear regression, decision trees, random forests, SVMs, k-means clustering — "
                    "all with a clean, consistent API: fit, predict, score. Start here. "
                    "For Deep Learning, you have two choices: PyTorch or TensorFlow. "
                    "My strong recommendation in 2026 is PyTorch. It has won the research community, "
                    "it is more Pythonic, easier to debug, and most new papers release code in PyTorch. "
                    "TensorFlow still has better production deployment tools, but PyTorch is catching up fast with TorchServe. "
                    "Finally, Jupyter Notebooks. Use them for experimentation and learning. "
                    "But please — do NOT write production code in notebooks. Learn to structure proper Python projects "
                    "with modules, packages, and version control from the beginning."
                ),
                "notes": "Practical advice slide. Students love tool recommendations. Show a quick Jupyter demo if time allows. Mention Google Colab as a free GPU option for students who do not have powerful laptops.",
                "wait_for_doubts": True
            },
            # ── SLIDE 4 ──────────────────────────────────────────────────
            {
                "slide_id": 4,
                "title": "Machine Learning Fundamentals — How Models Actually Learn",
                "content": (
                    "Okay, now we get to the exciting part. How does a machine actually learn? "
                    "Let me explain this with a simple example that every one of you can relate to. "
                    "Imagine you are trying to predict house prices in Bangalore. "
                    "You have data: square footage, number of bedrooms, distance from metro station, age of building. "
                    "These are your FEATURES — the inputs. The price is your TARGET — the output. "
                    "A machine learning model is a mathematical function that maps features to target. "
                    "Training is the process of finding the best parameters for that function using your historical data. "
                    "Now, there are three fundamental types of learning. "
                    "Supervised Learning: you have labeled data — input-output pairs. "
                    "The model learns to map inputs to known outputs. Classification (spam or not spam) "
                    "and Regression (predict a number like price) both fall here. This is 80 percent of real-world ML. "
                    "Unsupervised Learning: you have data but no labels. The model finds hidden patterns on its own. "
                    "Clustering customers into segments, anomaly detection, dimensionality reduction — these are unsupervised tasks. "
                    "Reinforcement Learning: an agent learns by interacting with an environment and receiving rewards or penalties. "
                    "This is how AlphaGo learned to play Go and how self-driving cars learn navigation policies. "
                    "It is the most complex type and you should tackle it last. "
                    "Now, the critical concept — overfitting vs underfitting. "
                    "Overfitting is when your model memorizes the training data instead of learning general patterns. "
                    "It gets 99 percent accuracy on training data but fails on new data. "
                    "Underfitting is when your model is too simple to capture the patterns in data. "
                    "The sweet spot is called the bias-variance tradeoff, and learning to balance it "
                    "is arguably the most important practical skill in machine learning. "
                    "We handle overfitting with techniques like regularization, dropout, cross-validation, "
                    "and simply getting more training data."
                ),
                "notes": "Core ML concepts slide. Use the house price example throughout — it grounds abstract concepts. Draw the underfitting-optimal-overfitting curves on the board. This is where students start to really 'get it'.",
                "wait_for_doubts": True
            },
            # ── SLIDE 5 ──────────────────────────────────────────────────
            {
                "slide_id": 5,
                "title": "Deep Learning & Neural Networks — The Architecture Revolution",
                "content": (
                    "Now let us level up to Deep Learning. "
                    "A neural network is inspired by — but NOT a copy of — the human brain. "
                    "It is made of layers of interconnected nodes called neurons. "
                    "Each neuron takes inputs, multiplies them by learned weights, adds a bias, "
                    "and passes the result through an activation function like ReLU or Sigmoid. "
                    "The magic is in the depth — when you stack many layers, "
                    "each layer learns increasingly abstract representations of the data. "
                    "For an image: the first layer might detect edges, the second layer detects textures, "
                    "the third layer detects parts like eyes and noses, and the final layer recognizes faces. "
                    "Now let me walk you through the key architectures you must know. "
                    "Convolutional Neural Networks — CNNs. These are designed for spatial data like images. "
                    "They use filters that slide across the image to detect local patterns. "
                    "This is what powers Google Photos face recognition, Tesla autopilot vision, and medical X-ray analysis. "
                    "Recurrent Neural Networks — RNNs and LSTMs. These process sequential data — text, time series, audio. "
                    "They have memory that carries information from previous time steps. "
                    "However, RNNs have largely been replaced by Transformers, which I will explain next. "
                    "Transformers — this is THE architecture of the 2020s. "
                    "The key innovation is the Attention mechanism — instead of processing sequences step by step, "
                    "Transformers can look at ALL positions in the input simultaneously. "
                    "This parallelism makes them dramatically faster to train and better at capturing long-range dependencies. "
                    "GPT, BERT, LLaMA, Gemini — all of these are Transformer-based models. "
                    "The original paper 'Attention Is All You Need' from 2017 is probably the most important "
                    "AI paper of the decade. I highly recommend reading it — it is only 15 pages. "
                    "For practical purposes: start with a simple feedforward network, "
                    "then build a CNN for image classification, then study the Transformer architecture. "
                    "That progression will give you a solid deep learning foundation."
                ),
                "notes": "The most technically dense slide. Go slow. Draw a simple 3-layer neural network on the board. Animate the forward pass. When explaining Transformers, use the analogy: RNN reads a book word by word, Transformer reads the entire page at once.",
                "wait_for_doubts": True
            },
            # ── SLIDE 6 ──────────────────────────────────────────────────
            {
                "slide_id": 6,
                "title": "Large Language Models & Prompt Engineering",
                "content": (
                    "Alright, this is the section everyone has been waiting for — Large Language Models. "
                    "ChatGPT, Gemini, Claude, LLaMA — these are all LLMs. "
                    "An LLM is essentially a very large Transformer model trained on massive amounts of text data. "
                    "GPT-4, for example, was trained on trillions of tokens from books, websites, and code repositories. "
                    "The training objective is deceptively simple: predict the next word. "
                    "Given 'The capital of France is', the model should predict 'Paris'. "
                    "But when you scale this simple objective to billions of parameters and trillions of training tokens, "
                    "something remarkable happens — the model develops emergent capabilities. "
                    "It can write code, solve math problems, translate languages, and even reason about abstract concepts — "
                    "all from just learning to predict the next word. This is called the scaling hypothesis. "
                    "Now, as an engineer, there are three levels of working with LLMs. "
                    "Level 1: Prompt Engineering. You use the model as-is through an API. "
                    "You craft your input prompts carefully to get the best outputs. "
                    "This includes techniques like few-shot prompting (giving examples in your prompt), "
                    "chain-of-thought prompting (asking the model to think step by step), "
                    "and system prompts (setting the model's persona and constraints). "
                    "Level 2: RAG — Retrieval-Augmented Generation. "
                    "The model does not know your company's internal documents. "
                    "RAG lets you fetch relevant documents from a database and inject them into the prompt context. "
                    "This is how most enterprise AI applications work in production. "
                    "Level 3: Fine-tuning. You take a pre-trained model and train it further on your own dataset. "
                    "This is expensive and complex but gives you maximum control. "
                    "For most of you starting out, Level 1 and Level 2 are where you should focus. "
                    "Fine-tuning is an advanced topic that requires significant compute resources."
                ),
                "notes": "High engagement slide. Every student has used ChatGPT but few understand how it works. The 'predict next word' revelation is always an eye-opener. Demo a quick RAG example if possible. Mention API costs — students need to know this.",
                "wait_for_doubts": True
            },
            # ── SLIDE 7 ──────────────────────────────────────────────────
            {
                "slide_id": 7,
                "title": "Building Your First AI Projects — A Portfolio That Gets You Hired",
                "content": (
                    "Let me be direct with you — no one will hire you based on Coursera certificates alone. "
                    "What gets you hired is a portfolio of projects that demonstrate real problem-solving skills. "
                    "I review resumes for our team and I can tell you exactly what impresses me. "
                    "Let me give you a three-project portfolio strategy that has worked for many of my mentees. "
                    "Project 1: A classical ML project with a real dataset. "
                    "Pick a problem from Kaggle — house price prediction, customer churn prediction, credit card fraud detection. "
                    "But do NOT just train a model. Do proper EDA — Exploratory Data Analysis. "
                    "Handle missing values, engineer features, try multiple algorithms, "
                    "compare their performance with proper cross-validation, and write a clean README explaining your approach. "
                    "This shows you understand the full ML pipeline, not just the model.fit() part. "
                    "Project 2: A deep learning project with deployment. "
                    "Build an image classifier or a sentiment analyzer. Train it in PyTorch. "
                    "Then — and this is where 90 percent of students stop — DEPLOY IT. "
                    "Wrap it in a FastAPI backend, create a simple frontend, containerize it with Docker, "
                    "and host it on a free tier cloud service. A deployed model is ten times more impressive than a notebook. "
                    "Project 3: An LLM-powered application. "
                    "Build something that uses the OpenAI or Gemini API with RAG. "
                    "A chatbot that answers questions from your college syllabus, "
                    "a resume analyzer that gives feedback, a code review assistant — something useful. "
                    "Use a vector database like ChromaDB, implement proper prompt engineering, "
                    "and handle edge cases like hallucinations and token limits. "
                    "Put all three projects on GitHub with clean code, proper documentation, and live demos. "
                    "This portfolio alone puts you ahead of 95 percent of applicants."
                ),
                "notes": "The most actionable slide. Students leave energized after this one. Be specific with project suggestions — vague advice is useless. Mention that contributing to open-source ML libraries is also extremely valuable. Share specific Kaggle competition names if possible.",
                "wait_for_doubts": True
            },
            # ── SLIDE 8 ──────────────────────────────────────────────────
            {
                "slide_id": 8,
                "title": "AI Ethics, Bias & Responsible Development",
                "content": (
                    "Before I let you go, I want to talk about something that does not get enough attention "
                    "in technical seminars — the ethical responsibility that comes with building AI systems. "
                    "This is not a soft topic. This has real engineering implications. "
                    "Let me give you three real examples. "
                    "Example 1: Amazon built a resume screening AI that was trained on 10 years of hiring data. "
                    "The model learned to penalize resumes that contained the word 'women's' — "
                    "like 'women's chess club' — because historically, Amazon had hired more men. "
                    "The model amplified existing bias in the data. They had to scrap the entire system. "
                    "Example 2: A healthcare AI model used in American hospitals was found to systematically "
                    "recommend less care for Black patients compared to white patients with the same conditions. "
                    "The bias? The model used healthcare SPENDING as a proxy for health needs. "
                    "Because of systemic inequities, Black patients historically had less money spent on their care, "
                    "so the model concluded they were healthier. The proxy metric was the problem. "
                    "Example 3: Facial recognition systems have been shown to have significantly higher error rates "
                    "for darker-skinned individuals and women, because the training datasets were dominated by "
                    "lighter-skinned male faces. "
                    "So what do you do about this as an engineer? "
                    "First, always audit your training data. Who collected it? Who is represented? Who is missing? "
                    "Second, test your model across different demographic groups before deployment. "
                    "Third, be transparent about your model's limitations. No model is perfect — "
                    "communicate what it can and cannot do. "
                    "Fourth, build feedback mechanisms so users can report when the AI is wrong. "
                    "And finally, remember that 'the algorithm decided' is never an acceptable excuse. "
                    "You built the algorithm. You chose the data. You are responsible."
                ),
                "notes": "End on a serious and thoughtful note. These examples always spark intense discussion. Encourage students to take an AI ethics course. Mention the EU AI Act and India's upcoming AI regulations as real policy frameworks they should be aware of.",
                "wait_for_doubts": True
            },
            # ── SLIDE 9 ──────────────────────────────────────────────────
            {
                "slide_id": 9,
                "title": "Your 6-Month Learning Roadmap & Resources",
                "content": (
                    "Alright, let me wrap up with a concrete 6-month roadmap that you can start today. "
                    "Month 1: Python foundations. Complete the Python section on freeCodeCamp or Corey Schafer's YouTube series. "
                    "Practice on LeetCode Easy problems — not for interviews, but to build coding fluency. "
                    "Get comfortable with NumPy, Pandas, and Matplotlib. "
                    "Month 2: Mathematics refresh. Take 3Blue1Brown's 'Essence of Linear Algebra' series — "
                    "it is free, visual, and the best resource I have ever seen for building mathematical intuition. "
                    "Supplement with Khan Academy for calculus and probability. "
                    "Month 3: Classical Machine Learning. Take Andrew Ng's Machine Learning Specialization on Coursera. "
                    "It has been updated for 2024 and it is still the gold standard. "
                    "Simultaneously, start your first Kaggle project. "
                    "Month 4: Deep Learning. Take the Deep Learning Specialization — also by Andrew Ng. "
                    "Build your CNN image classifier project. Start learning PyTorch through the official tutorials. "
                    "Month 5: LLMs and Applications. Study the Transformer architecture. "
                    "Read 'Attention Is All You Need'. Build your RAG application. "
                    "Start using LangChain or LlamaIndex for building LLM pipelines. "
                    "Month 6: Portfolio polish and job preparation. "
                    "Deploy all projects, write blog posts about what you learned, "
                    "contribute to one open-source ML project, and start applying. "
                    "Free resources I recommend: fast.ai for practical deep learning, "
                    "Andrej Karpathy's YouTube channel for understanding neural networks from scratch, "
                    "Hugging Face documentation for working with pre-trained models, "
                    "and Papers With Code for staying current with research. "
                    "Remember — consistency beats intensity. One hour every day is better than "
                    "ten hours on a weekend. Build the habit. "
                    "Thank you for your time. I am excited to see what you all build. Let us do final questions."
                ),
                "notes": "Closing slide with maximum practical value. Students will photograph this slide. Keep the resources specific and free wherever possible. End with energy and encouragement. Open the floor for general questions.",
                "wait_for_doubts": False
            }
        ]
    }

    # ─── QUESTIONS (Realistic seminar doubts per slide) ──────────────────
    # Organized by which slide they are most relevant to
    slide_questions = {
        1: [  # "What Exactly Is AI?"
            "Sir, you mentioned Narrow AI vs AGI. Is AGI even possible, or is it just science fiction?",
            "What is the difference between AI and automation? Like, is a rule-based chatbot considered AI?",
            "Where does Reinforcement Learning fit in the AI > ML > DL hierarchy you showed?",
            "Are models like ChatGPT actually 'intelligent' or are they just very good at pattern matching?",
            "Can you explain what a neural network is in one simple sentence?",
            "Is data science the same thing as machine learning or are they different fields?"
        ],
        2: [  # "Mathematics You Need"
            "I am from a CS branch and my math is weak. Can I still get into AI realistically?",
            "How much linear algebra do I need to understand before starting with neural networks?",
            "You mentioned gradient descent — can you explain it with a simple real-world analogy?",
            "Is statistics more important than calculus for someone who wants to do applied ML, not research?",
            "Do I need to understand proofs and theorems, or just the intuition behind the math?",
            "What are eigenvalues used for in machine learning? I studied them but never understood why they matter."
        ],
        3: [  # "Python & Tools"
            "Should I learn Python from scratch or is knowing C/C++ from college enough to start ML?",
            "What is the difference between PyTorch and TensorFlow in practical terms? Which one should I learn first?",
            "Is Google Colab good enough for deep learning projects or do I need to buy a GPU laptop?",
            "How important is knowing Git and version control for ML projects?",
            "Can you explain when to use Jupyter notebooks versus regular Python scripts?",
            "Are there any good free alternatives to paid tools like Weights and Biases for experiment tracking?"
        ],
        4: [  # "ML Fundamentals"
            "In the house price example, how do you decide which features to include and which to ignore?",
            "What is the practical difference between classification and regression? Can you give examples?",
            "How do you know if your model is overfitting? What are the warning signs?",
            "You mentioned cross-validation — what is it and why is it better than a simple train-test split?",
            "How much training data do you typically need for a machine learning model to work well?",
            "Sir, what is regularization? You mentioned it prevents overfitting but how does it actually work?",
            "Which algorithm should a beginner start with — linear regression, decision trees, or something else?"
        ],
        5: [  # "Deep Learning & Neural Networks"
            "How is a neural network different from traditional machine learning algorithms like random forests?",
            "What is an activation function and why can't we just use a linear function throughout the network?",
            "You mentioned CNNs detect edges and textures — how does that actually happen technically?",
            "Why have Transformers replaced RNNs? What was wrong with RNNs?",
            "What does 'Attention Is All You Need' mean? What is the attention mechanism in simple terms?",
            "How many layers and neurons should I use when designing a neural network? Is there a rule of thumb?",
            "What is backpropagation? I have heard the term but never understood how it actually trains the network."
        ],
        6: [  # "LLMs & Prompt Engineering"
            "If LLMs just predict the next word, how can they solve complex reasoning and math problems?",
            "What is the difference between GPT, BERT, and LLaMA? Are they all the same type of model?",
            "How does RAG actually work? How do you connect a database to an LLM?",
            "What is fine-tuning and when should I use it instead of prompt engineering?",
            "How do LLMs handle hallucinations? Is there a reliable way to prevent them?",
            "What are tokens and why do LLMs have context limits? Why can't they process unlimited text?",
            "Is it possible to run an LLM locally on my laptop or do I always need cloud APIs?"
        ],
        7: [  # "Building Projects"
            "How do I pick a good Kaggle project for my resume? There are thousands of competitions.",
            "What is the best way to deploy a machine learning model for free as a student?",
            "Should I focus on one domain like NLP or computer vision, or should I try everything?",
            "How important are internships versus personal projects when applying for AI roles?",
            "What does a typical AI engineer interview look like? Is it all coding or also theory?",
            "Sir, I do not have a GPU and cannot afford cloud computing. How do I train deep learning models?"
        ],
        8: [  # "AI Ethics & Bias"
            "How do you actually detect bias in a dataset before training a model on it?",
            "Is it possible to make a completely unbiased AI model, or is some bias always inevitable?",
            "Who should be held responsible when an AI system causes harm — the developer, the company, or the user?",
            "Are there any regulations in India right now that govern how AI systems can be used?",
            "How do you handle bias when the training data itself reflects real-world inequalities?",
            "What is explainable AI and why is it important for ethical AI deployment?"
        ]
    }

    # ─── EXECUTE ─────────────────────────────────────────────────────────
    try:
        # 1. Start seminar (active slide = 0)
        print("\n1. Starting seminar...")
        r = requests.post(f"{BASE_URL}/seminar/start", json=ai_deck)
        if r.status_code != 200:
            print(f"   FAILED: {r.text}")
            return
        print("   Seminar started successfully.")

        # 2. We want to test questions on a slide with wait_for_doubts=True.
        #    Advance to slide 1 where doubts are accepted.
        print("\n2. Advancing to Slide 1 (What Exactly Is AI?)...")
        r = requests.post(f"{BASE_URL}/seminar/next")
        if r.status_code != 200:
            print(f"   FAILED to advance: {r.text}")
            return

        status = requests.get(f"{BASE_URL}/seminar/status").json()
        print(f"   Active slide: {status['current_slide_id']} - {status['title']}")

        # 3. Submit ALL questions to the active slide (slide 1)
        #    This simulates a real seminar Q&A where all questions come in at once
        all_questions = []
        for slide_id, questions in slide_questions.items():
            for q in questions:
                all_questions.append(q)

        print(f"\n3. Submitting {len(all_questions)} realistic student questions...")
        submitted = 0
        for q in all_questions:
            r = requests.post(f"{BASE_URL}/doubts/submit", json={"slide_id": 1, "question": q})
            if r.status_code == 200:
                submitted += 1
            else:
                print(f"   WARN: Failed to submit '{q[:50]}...' — {r.text}")
        print(f"   Successfully submitted {submitted}/{len(all_questions)} questions.")

        # 4. Query ranked doubts for Slide 1 with top_n=3
        print(f"\n4. Querying RAG analysis for Slide 1 (top_n=3)...")
        r = requests.get(f"{BASE_URL}/doubts/slide/1/rank?top_n=3&global_pool=true")
        if r.status_code == 200:
            ranked = r.json()
            print(f"   Total doubts analyzed: {len(ranked)}")

            # Group by category for clean display
            categories = {}
            for d in ranked:
                cat = d["category"]
                if cat not in categories:
                    categories[cat] = []
                categories[cat].append(d)

            for cat_name, cat_label in [
                ("top_n", "TOP N — Most Relevant to Current Slide"),
                ("low_priority", "LOW PRIORITY — Relevant but Outside Top N"),
                ("diff_slide", "DIFFERENT SLIDE — Covered Elsewhere"),
                ("not_relevant_to_ppt", "NOT RELEVANT TO PPT")
            ]:
                doubts_in_cat = categories.get(cat_name, [])
                if doubts_in_cat:
                    print(f"\n   [+] {cat_label} ({len(doubts_in_cat)} questions)")
                    for i, d in enumerate(doubts_in_cat):
                        print(f"   |   [{i+1}] \"{d['question'][:80]}{'...' if len(d['question']) > 80 else ''}\"")
                        print(f"   |       Score: {d['similarity_score']:.4f} | Best Slide: {d['best_matching_slide_id']} | Message: {d['message']}")
                    print(f"   [_]")
        else:
            print(f"   FAILED: {r.text}")

        # 5. Also query for Slide 5 (Deep Learning) to show different routing
        print(f"\n5. Querying RAG analysis for Slide 5 (top_n=3)...")
        r = requests.get(f"{BASE_URL}/doubts/slide/5/rank?top_n=3&global_pool=true")
        if r.status_code == 200:
            ranked = r.json()
            print(f"   Total doubts analyzed: {len(ranked)}")

            categories = {}
            for d in ranked:
                cat = d["category"]
                if cat not in categories:
                    categories[cat] = []
                categories[cat].append(d)

            for cat_name, cat_label in [
                ("top_n", "TOP N — Most Relevant to Current Slide (Slide 5: Deep Learning)"),
                ("low_priority", "LOW PRIORITY — Relevant but Outside Top N"),
                ("diff_slide", "DIFFERENT SLIDE — Covered Elsewhere"),
                ("not_relevant_to_ppt", "NOT RELEVANT TO PPT")
            ]:
                doubts_in_cat = categories.get(cat_name, [])
                if doubts_in_cat:
                    print(f"\n   [+] {cat_label} ({len(doubts_in_cat)} questions)")
                    for i, d in enumerate(doubts_in_cat):
                        print(f"   |   [{i+1}] \"{d['question'][:80]}{'...' if len(d['question']) > 80 else ''}\"")
                        print(f"   |       Score: {d['similarity_score']:.4f} | Best Slide: {d['best_matching_slide_id']} | Message: {d['message']}")
                    print(f"   [_]")
        else:
            print(f"   FAILED: {r.text}")

        print("\n" + "=" * 80)
        print("  SEMINAR LOADED SUCCESSFULLY!")
        print(f"  Deck: {ai_deck['title']}")
        print(f"  Slides: {len(ai_deck['slides'])}")
        print(f"  Questions submitted: {submitted}")
        print(f"  Dashboard: http://localhost:8000/")
        print(f"  Rank API: http://localhost:8000/api/v1/doubts/slide/1/rank?top_n=3&global_pool=true")
        print("=" * 80)

    except requests.exceptions.ConnectionError:
        print("ERROR: Cannot connect to http://localhost:8000/. Is the server running?")
        print("Start it with: python run.py")

if __name__ == "__main__":
    load_ai_seminar()
