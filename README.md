# 🛒 SWYFTCART – E-commerce Platform  

[![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python&logoColor=white)](https://www.python.org/)  
[![Django](https://img.shields.io/badge/Django-5.0-green?logo=django&logoColor=white)](https://www.djangoproject.com/)  
[![PayPal](https://img.shields.io/badge/Payments-PayPal-00457C?logo=paypal&logoColor=white)](https://paypal.com/)  
[![Deployment](https://img.shields.io/badge/Deployed%20on-Vercel-black?logo=vercel)](https://vercel.com/)  
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)  

SWYFTCART is a full-featured **E-commerce web application** built with **Django** and deployed on **Vercel**.  
It provides users with a smooth shopping experience, including browsing, cart management, checkout, **PayPal payments**, and order tracking.  

---

## 🌐 Demo  

🔗 **Live Website:** [SWYFTCART on Vercel](https://your-vercel-app-link.vercel.app)  
*(Replace with your actual Vercel deployment link)*  

---

## 🚀 Features  

- **User Accounts & Authentication**  
  - Registration, Login, Logout  
  - Profile Management  

- **Product Management**  
  - Categories & Subcategories  
  - Product Search & Filtering  
  - Top-rated / Featured products display  

- **Cart & Orders**  
  - Add / Remove / Update items in cart  
  - Price filtering and pagination  
  - Checkout & Order summary  
  - Order history tracking  

- **Payments**  
  - **PayPal integration** for secure online transactions  

- **Admin Panel (Django Admin)**  
  - Manage products, categories, users, and orders  
  - View customer contact messages  

- **Responsive Design**  
  - Mobile-friendly and attractive UI with modern CSS  

- **Deployment**  
  - Hosted on **Vercel** for fast and reliable performance  

---

## 🛠️ Tech Stack  

- **Backend:** Django, Python  
- **Frontend:** HTML, CSS, Bootstrap, JavaScript  
- **Payments:** PayPal SDK  
- **Database:** SQLite (default) / PostgreSQL (production ready)  
- **Deployment:** Vercel  
- **Environment Management:** `dotenv`  

---

## 📂 Project Structure  

SWYFTCART/
│── accounts/ # User authentication & profiles
│── carts/ # Shopping cart app
│── category/ # Product categories
│── env/ # Virtual environment (not tracked in Git)
│── media/ # Media uploads
│── orders/ # Order management
│── static/ # CSS, JS, Images
│── store/ # Product store logic
│── Swyftcart/ # Project configuration
│── templates/ # HTML templates
│── manage.py # Django management script
│── requirements.txt # Python dependencies
│── db.sqlite3 # SQLite database
│── .env # Environment variables



---

## ⚙️ Installation & Setup  

### 1️⃣ Clone the Repository  

- git clone https://github.com/your-username/swyftcart.git
- cd swyftcart

### 2️⃣ Create Virtual Environment
- python -m venv env
- source env/bin/activate   # On Linux/Mac
- env\Scripts\activate      # On Windows


### 3️⃣ Install Dependencies
- pip install -r requirements.txt

### 4️⃣ Set Up Environment Variables
- Create a .env file in the root directory:
- SECRET_KEY=your-secret-key
- DEBUG=True
- ALLOWED_HOSTS=127.0.0.1,localhost

**PayPal settings**
- PAYPAL_CLIENT_ID=your-client-id
- PAYPAL_SECRET_KEY=your-secret-key

### 5️⃣ Run Migrations
- python manage.py migrate

### 6️⃣ Create Superuser
- python manage.py createsuperuser

### 7️⃣ Start Development Server
- python manage.py runserver


- Now visit 👉 http://127.0.0.1:8000/

---


## 🌍 Deployment on Vercel

- Push your code to GitHub
- Connect your GitHub repo to Vercel
- Add environment variables (.env) in Vercel dashboard
- Deploy automatically with every push 🚀

## 🖼️ Screenshots:
<img width="1920" height="1039" alt="Image" src="https://github.com/user-attachments/assets/71e4902c-c383-4505-b1a0-762bb7bb438a" />


<img width="1920" height="1042" alt="Image" src="https://github.com/user-attachments/assets/16ba366c-05df-437c-bf39-c4306059b2fb" />


<img width="1920" height="1035" alt="Image" src="https://github.com/user-attachments/assets/0c9225b2-4cdc-4e5f-b848-801210e7043e" />


<img width="1920" height="990" alt="Image" src="https://github.com/user-attachments/assets/e90ee1cc-1547-44f2-a3d0-572941c7e128" />


<img width="1920" height="1027" alt="Image" src="https://github.com/user-attachments/assets/d95724de-13e4-4e24-9749-bca8268fbe7c" />


<img width="1920" height="1030" alt="Image" src="https://github.com/user-attachments/assets/b7068874-f5f6-454d-9482-8d629f3f9644" />



## 📊 Performance & Accessibility

Tested with Google Lighthouse 🔦
- ✅ Performance: 90+
- ✅ Accessibility: 95+
- ✅ Best Practices: 100
- ✅ SEO: 90+

## 🤝 Contributing

- Contributions are welcome!
- Fork the repo
- Create a feature branch (git checkout -b feature-name)
- Commit changes (git commit -m "Added new feature")
- Push to branch (git push origin feature-name)
- Open a Pull Request


## 📜 License

This project is licensed under the MIT License – feel free to use and modify it.


