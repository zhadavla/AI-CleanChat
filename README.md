# AI-Driven Webchat with Real-Time Harmful Content Prediction

This project is an AI-powered webchat application that includes real-time harmful content prediction. It allows users to engage in chat conversations while the system continuously monitors and predicts harmful or inappropriate content. 

## Features

- **Real-Time Content Moderation**: Automatically detects and flags harmful messages for review.
- **User-Driven Feedback**: Users can manually classify messages as good or bad, improving the model's performance over time.
- **Async WebSocket Communication**: Supports real-time messaging between users.
- **Frontend/Backend Separation**: The application is designed with a FastAPI backend and a JavaScript frontend, with WebSocket technology for live updates.
- **Deployed in Docker**: Easily deployable using Docker containers, and trained on Google Cloud with CUDA for BERT model optimization.
  
## Screenshot
![Chat Application Screenshot](./screenshots/img.png)
The second Artem's message is blured because it is harmful content (by the models' opinion). Every user can mark the message as harmful or not harmful. The model will learn from the feedbacks and improve itself.
![Chat Application Screenshot](./screenshots/img_1.png)
By the Artem's feedback, the message is just friendly joke, so he marked it as not harmful.
![Chat Application Screenshot](./screenshots/img_2.png)
But Vlad thinks otherwise, so he marked the message as harmful.
![Chat Application Screenshot](./screenshots/img_3.png)
Both feedbacks will be sent to the model, so it can learn from them and improve itself.

## How It Works

- **Message Filtering**: A finetuned BERT model analyzes chat messages in real time and predicts whether the content is harmful or inappropriate.
- **User Feedback Loop**: Users can provide feedback on flagged messages by marking them as appropriate or inappropriate, allowing the AI to continuously learn and adapt to the conversation style.
- **WebSocket for Real-Time Communication**: Messages are sent and received instantly using WebSockets, creating a smooth, real-time chat experience.
  
## Technologies Used

- **Backend**: FastAPI, WebSockets
- **Frontend**: JavaScript, WebSockets
- **Machine Learning**: BERT model, finetuned for harmful content prediction
- **Deployment**: Docker, Google Cloud (CUDA for training)
- **Testing**: pytest for WebSocket behavior and backend functionality

## Getting Started

To run the application locally, follow these steps:

1. Build the Docker containers:

    ```bash
    docker-compose up --build
    ```

2. Access the application:

    Open your browser and navigate to `http://localhost:8000` to use the chat application.

## Contributing

Also, you can access a chat by following the link below:
https://clean-chat-backend-534372344465.us-central1.run.app/