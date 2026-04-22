# TravelEase - Hassle-Free Travel Planning

TravelEase is a web application that helps users plan their travel itineraries. Users can register, log in, input their travel details (source, destination, dates), and receive a planned itinerary along with weather information for their destination.

## Features

*   User Registration and Login
*   Personalized Travel Planning
*   Weather Information for Destination
*   Itinerary Generation (integrates with external APIs for weather and can be extended for LLM-based itinerary generation)
*   Download Itinerary as PDF
*   Contact Form
*   About Us Page

## Technologies Used

*   **Backend:** Python (Flask)
*   **Frontend:** HTML, CSS, JavaScript (Bootstrap for styling)
*   **Database:** SQLite
*   **External APIs:** Visual Crossing Weather API (requires an API key)
*   **Libraries:** `requests`, `markdown2`, `html2pdf.js`

## Obtain API Keys
*   **Visual Crossing Weather API:**
        Go to Visual Crossing Weather Data.
        Sign up for a free account.
        Generate an API key.
        Replace 'YOUR_VISUAL_CROSSING_API_KEY' in app.py with your actual API key.

*   **EmailJS (for Contact Form):**
        Go to EmailJS.
        Sign up and create a new Email Service and Email Template.
        Note your Public Key, Service ID, and Template ID.
        Replace 'Public Key', 'service_id', and 'template_id' in templates/contact.html with your actual keys.

## Setup Instructions

### 1. Clone the Repository

```bash
git clone <your-repository-url>
cd TravelEase

