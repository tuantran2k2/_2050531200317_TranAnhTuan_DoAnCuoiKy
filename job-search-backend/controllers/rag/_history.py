# import json
# import os

# import _constants


# ############################################################################################################
# # Save history
# def save_history(user_id, query, answer, collection_id, chatbot_name, base64_images=""):
   
#     _path = _constants.DATAS_PATH

#     path = _path + "/" + chatbot_name
#     os.makedirs(path, exist_ok=True)

#     user_history_file = os.path.join(
#         _path, chatbot_name, f"history_{user_id}_{collection_id}.json"
#     )
#     history = []
#     if os.path.exists(user_history_file):
#         with open(user_history_file, "r", encoding="utf-8") as file:
#             try:
#                 history = json.load(file)
#             except json.JSONDecodeError:
#                 print(f"Error decoding JSON from file: {user_history_file}")
#                 pass

#     # Append new query and answer
#     history.append({"query": query, "answer": answer, "base64_images": "", "chart_answer": ""})

#     # Limit the total number of entries to 20
#     if len(history) > 20:
#         history = history[-20:]

#     # Process answers to keep only the 3 most recent ones
#     for entry in history[:-3]:
#         entry["answer"] = ""

#     # Save history back to file
#     with open(user_history_file, "w", encoding="utf-8") as file:
#         json.dump(history, file, indent=4)


# def save_history_public(
#         user_id, query, answer, collection_id, chatbot_name, base64_images="", chart_answer=""
# ):
#     _path = _constants.DATAS_PATH

#     # Tạo đường dẫn đến thư mục người dùng và bộ sưu tập
#     user_directory = os.path.join(_path_public, chatbot_name, str(user_id))
#     os.makedirs(user_directory, exist_ok=True)

#     # Tạo đường dẫn đến tệp lịch sử
#     user_history_file = os.path.join(
#         user_directory, f"history_{user_id}_{collection_id}.json"
#     )
#     # print(user_history_file)

#     history = []
#     if os.path.exists(user_history_file):
#         with open(user_history_file, "r", encoding="utf-8") as file:
#             try:
#                 history = json.load(file)
#             except json.JSONDecodeError:
#                 print(f"Error decoding JSON from file: {user_history_file}")
#                 pass

#     original, clarified = _re_write_query.extract_questions(query)
#     history.append(
#         {"query": original, "answer": answer, "base64_images": base64_images, "chart_answer": chart_answer}
#     )

#     with open(user_history_file, "w", encoding="utf-8") as file:
#         json.dump(history, file, indent=4)

#     if history:
#         conversation_name_file = os.path.join(
#             user_directory, f"history_{user_id}_{collection_id}.txt"
#         )
#         with open(conversation_name_file, "w", encoding="utf-8") as file:
#             file.write(str(answer))

#     path = _path + "/" + chatbot_name
#     os.makedirs(path, exist_ok=True)

#     user_history_file = os.path.join(
#         _path, chatbot_name, f"history_{user_id}_{collection_id}.json"
#     )


# # ############################################################################################################
# # # Save history
# # def save_history_mekong(user_id, query, answer, collection_id, chatbot_name, base64_images):
# #     path = _constants.DATAS_MEKONGAI_PATH + "/" + chatbot_name
# #     os.makedirs(path, exist_ok=True)
# #
# #     user_history_file = os.path.join(_constants.DATAS_MEKONGAI_PATH, chatbot_name, f"history_{user_id}_{collection_id}.json")
# #     history = []
# #     if os.path.exists(user_history_file):
# #         with open(user_history_file, "r", encoding="utf-8") as file:
# #             try:
# #                 history = json.load(file)
# #             except json.JSONDecodeError:
# #                 print(f"Error decoding JSON from file: {user_history_file}")
# #                 pass
# #
# #     # Append new query and answer
# #     history.append({"query": query, "answer": answer, "base64_images": ""})
# #
# #     # Limit the total number of entries to 20
# #     if len(history) > 20:
# #         history = history[-20:]
# #
# #     # Process answers to keep only the 3 most recent ones
# #     for entry in history[:-3]:
# #         entry["answer"] = ""
# #
# #     # Save history back to file
# #     with open(user_history_file, "w", encoding="utf-8") as file:
# #         json.dump(history, file, indent=4)
# #
# #
# # def save_history_mekong_public(user_id, query, answer, collection_id, chatbot_name, base64_images):
# #     # Tạo đường dẫn đến thư mục người dùng và bộ sưu tập
# #     user_directory = os.path.join(_constants.DATAS_MEKONGAI_PUBLIC_PATH, chatbot_name, str(user_id))
# #     os.makedirs(user_directory, exist_ok=True)
# #
# #     # Tạo đường dẫn đến tệp lịch sử
# #     user_history_file = os.path.join(user_directory, f"history_{user_id}_{collection_id}.json")
# #     # print(user_history_file)
# #
# #     history = []
# #     if os.path.exists(user_history_file):
# #         with open(user_history_file, "r", encoding="utf-8") as file:
# #             try:
# #                 history = json.load(file)
# #             except json.JSONDecodeError:
# #                 print(f"Error decoding JSON from file: {user_history_file}")
# #                 pass
# #
# #     original, clarified = _re_write_query.extract_questions(query)
# #     history.append({"query": original, "answer": answer, "base64_images": base64_images})
# #
# #     with open(user_history_file, "w", encoding="utf-8") as file:
# #         json.dump(history, file, indent=4)
# #
# #     if history:
# #         conversation_name_file = os.path.join(user_directory, f"history_{user_id}_{collection_id}.txt")
# #         with open(conversation_name_file, "w", encoding="utf-8") as file:
# #             file.write("")
# #
# #     path = _constants.DATAS_MEKONGAI_PATH + "/" + chatbot_name
# #     os.makedirs(path, exist_ok=True)
# #
# #     user_history_file = os.path.join(_constants.DATAS_MEKONGAI_PATH, chatbot_name, f"history_{user_id}_{collection_id}.json")
# #     history = []
# #     if os.path.exists(user_history_file):
# #         with open(user_history_file, "r", encoding="utf-8") as file:
# #             try:
# #                 history = json.load(file)
# #             except json.JSONDecodeError:
# #                 print(f"Error decoding JSON from file: {user_history_file}")
# #                 pass
# #
# #     # Append new query and answer
# #     history.append({"query": query, "answer": answer, "base64_images": ""})
# #
# #     # Limit the total number of entries to 20
# #     if len(history) > 20:
# #         history = history[-20:]
# #
# #     # Process answers to keep only the 3 most recent ones
# #     for entry in history[:-3]:
# #         entry["answer"] = ""
# #
# #     # Save history back to file
# #     with open(user_history_file, "w", encoding="utf-8") as file:
# #         json.dump(history, file, indent=4)


# ############################################################################################################
# # Load history
# def load_history(user_id, collection_id, chatbot_name):
#     _path = _constants.DATAS_PATH

#     user_history_file = os.path.join(
#         _path, chatbot_name, f"history_{user_id}_{collection_id}.json"
#     )
#     if not os.path.exists(user_history_file):
#         return []

#     if os.path.getsize(user_history_file) == 0:
#         return []

#     with open(user_history_file, "r", encoding="utf-8") as file:
#         try:
#             history = json.load(file)
#         except json.JSONDecodeError:
#             print(f"Error decoding JSON from file: {user_history_file}")
#             return []

#     return history


# # Load all history for public conversations
# def load_history_public(user_files, chatbot_name):
#     user_histories = []
#     seen_collections = set()

#     if chatbot_name == _constants.NAME_CHATBOT_MEKONGAI:
#         _path = _constants.DATAS_MEKONGAI_PUBLIC_PATH
#     else:
#         _path = _constants.DATAS_PUBLIC_PATH

#     for file_name in user_files:
#         parts = file_name.split(".")[0].split("_")
#         user_id = parts[1]
#         collection_id = parts[-1]

#         if collection_id in seen_collections:
#             continue

#         json_file_path = os.path.join(
#             _path, chatbot_name, f"{user_id}", f"history_{user_id}_{collection_id}.json"
#         )
#         txt_file_path = os.path.join(
#             _path, chatbot_name, f"{user_id}", f"history_{user_id}_{collection_id}.txt"
#         )
#         if os.path.exists(json_file_path) and os.path.exists(txt_file_path):
#             with open(json_file_path, "r", encoding="utf-8") as json_file:
#                 json_content = json.load(json_file)
#             with open(txt_file_path, "r", encoding="utf-8") as txt_file:
#                 txt_content = txt_file.read()

#             user_histories.append(
#                 {
#                     "collection_id": str(collection_id),
#                     "content": json_content,
#                     "name": txt_content,
#                 }
#             )

#             seen_collections.add(collection_id)

#     return user_histories
