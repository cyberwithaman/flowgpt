# 🌊 FlowGPT

A visual automation tool using LangGraph state and edge flows. This Django application allows you to define and run task pipelines using LangGraph's node-based logic.

## ✨ Features

- **🧠 Admin Panel**: Define pipelines, nodes, and their connections
- **👤 User Interface**: Select and run pipelines with input data
- **📊 Visual Progress**: Track pipeline execution through LangGraph nodes
- **⚙️ Rule-based Functions**: Text cleaning, summarization, translation, and more
- **📈 Admin Dashboard**: Visualize analytics for all models with charts and graphs

## 🚀 Installation

1. Clone the repository:
```
git clone https://github.com/cyberwithaman/flowgpt.git
cd flowgpt
```

2. Create and activate a virtual environment:
```
python -m venv venv
venv\Scripts\activate
```

3. Install dependencies:
```
pip install -r requirements.txt
```

4. Run migrations:
```
python manage.py migrate
```

5. Create a superuser:
```
python manage.py createsuperuser
```

## 🏃‍♂️ Quick Setup & Demo

To quickly set up sample data and see the demo in one command:

```
python manage.py setup_and_demo
```

Or use the provided scripts:
- Windows: `setup_and_demo.bat`

This will:
1. Load all sample data (nodes, pipelines, executions, contacts)
2. Run the demo showing pipeline configurations
3. Provide instructions for accessing the admin dashboard

## 📦 Loading Sample Data

To only load the sample data without running the demo:

```
python manage.py load_sample_data
```

This will create:
- Sample nodes (Text Cleaner, Uppercase Converter, Basic Summarizer, Translators, Email Sender)
- Sample pipelines with connections
- Example pipeline executions
- Sample contact messages

## 🎮 Demo Mode

> **Note**: The direct pipeline execution demo currently requires updates to match the latest LangGraph API. The web interface using the Django views still functions correctly.

To view the pipeline configuration data without executing:

```
python manage.py run_demo
```

## 🖥️ Running the Application

Start the development server:

```
python manage.py runserver
```

Access the application at http://localhost:8000 and the admin interface at http://localhost:8000/admin

## 📊 Admin Dashboard

FlowGPT includes a comprehensive analytics dashboard that provides visualizations for all models:

- 🔍 Access the dashboard at http://localhost:8000/admin/dashboard/ (requires staff login)
- 📊 View charts for Contacts, Nodes, Pipelines, Edges, Executions, and Execution Steps
- 📉 Monitor key metrics and statistics with interactive visualizations
- 📈 See trends and patterns in your workflow data

## 🛠️ Using the Application

1. **👩‍💼 Admin Panel** (`/admin`):
   - Log in with your superuser credentials
   - Manage pipelines, nodes, and view execution history
   - View contact submissions
   - Access the analytics dashboard

2. **🏠 Home Page** (`/`):
   - Select a pipeline from the dropdown
   - Enter input text
   - Run the pipeline and view progress in real-time

3. **📬 Contact Page** (`/contact`):
   - Send messages through the contact form

## 🔄 LangGraph Compatibility

This application was designed with an earlier version of LangGraph. If you encounter API compatibility issues:

1. Check your installed LangGraph version with `pip show langgraph`
2. Review the `pipeline_executor.py` file to update the StateGraph API calls
3. Consult the [LangGraph documentation](https://langchain-ai.github.io/langgraph/) for the latest API

## 🧩 Pipeline Nodes

The application includes the following node types:

- **🧹 Clean Text**: Removes extra whitespace, URLs, and special characters
- **🔠 Convert to Uppercase**: Transforms text to uppercase
- **📝 Basic Summary**: Creates a simple summary using the first few sentences
- **🌐 Translate**: Performs basic dictionary-based translation (supports Spanish, French, German)
- **📧 Send Email**: Mocks sending an email with processed text

## 🔄 Pipeline State Flow

The LangGraph workflow manages state with these key attributes:
- `text`: The main text being processed
- `summary`: Generated text summary
- `translated_text`: Translation result
- `email_result`: Email sending status
- `metadata`: Processing timestamps and configuration details

## 💻 Technology Stack

- 🐍 Django (Backend)
- 🔄 LangGraph (Flow execution)
- 🗃️ SQLite3 (Database)
- 🎨 Bootstrap (Frontend)
- 📊 Matplotlib/Pandas (Analytics)

### 🔗 Connect with Me  
<p align="center">
  <a href="mailto:amananiloffial@gmail.com"><img src="https://img.icons8.com/color/48/000000/gmail-new.png" alt="Email"/></a>
  <a href="tel:+917892939127"><img src="https://img.icons8.com/color/48/000000/phone.png" alt="Phone"/></a>
  <a href="https://www.instagram.com/cyberwithaman"><img src="https://img.icons8.com/color/48/000000/instagram-new.png" alt="Instagram"/></a>
  <a href="https://wa.me/+917892939127"><img src="https://img.icons8.com/color/48/000000/whatsapp--v1.png" alt="WhatsApp"/></a>
  <a href="https://github.com/cyberwithaman"><img src="https://img.icons8.com/ios-filled/48/ffffff/github.png" style="background-color:#181717; border-radius:50%; padding:6px;" alt="GitHub"/></a>
  <a href="https://www.linkedin.com/in/cyberwithaman"><img src="https://img.icons8.com/color/48/000000/linkedin.png" alt="LinkedIn"/></a>
</p>
