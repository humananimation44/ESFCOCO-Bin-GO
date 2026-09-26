# ESFCOCO-Bin-GO
Team Members: Neel LUNIA, Hector YEUNG, Mitt NGAN.

We used MediaPipe Hands, an already existing, trained landmark detection model for real-time palm, finger, and hand tracking using the client's webcam. Our team used an integrated model in  a Python and OpenCV demo, selected the interaction flow, adapted the code, did multiple tests for tracking, and implemented reward zone logic. We had to run it locally on a computer because GitHub simply cannot run a webcam, and it needed to have a webcam.

We also utilized Perplexity as a learning and coding assistant for brainstorming, explaining Mediapip/OpenCV concepts, and troubleshooting; we did not train the underlying hand model. Other than OpenCV code, we used Perplexity simply to troubleshoot in extreme cases, with minimal use, and Copilot in VS Code Studio for debugging, as well as open-source HTML (very minimal use, however) for embedding the Python code into our HTML; we used heavy assistance from Copilot and a YouTube video to use Flask to connect the two languages.

OpenCV Code explanation-
Adopting the camera-tracking model from MediaPipe, we added visuals using simple borders, added functionality to the fingers, and added tracking with if, elif, and else to have a functional bin.

MediaPipe Hands: https://mediapipe.readthedocs.io/en/latest/solutions/hands.html

Description : 

