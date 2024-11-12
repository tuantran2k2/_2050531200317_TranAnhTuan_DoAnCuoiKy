from controllers import _cv


data = _cv.extract_text_from_pdf("D:/MEKONGAI/mekongai-social-media-bot/files/tests/CV_intern.pdf")

ans = _cv.chatbot_cv(data)


print(ans)