def chatbot():
    question = request.form['question']
    article_id = request.form['article_id']  
    article = articles_collection.find_one({"_id": article_id})

    if article and question in article['text_content']:
        return jsonify({"answer": "Here is the information you need: " + article['summary']})
    else:
        return jsonify({"answer": "I can only answer questions related to the current article."})

@app.route('/quiz', methods=['POST'])
def quiz():
    user_id = request.form['user_id']
    user_answer = request.form['answer']

    # Simulating questions
    questions = [
        {"question": "What is the capital of France?", "answer": "Paris"},
        {"question": "Who wrote '1984'?", "answer": "George Orwell"},
    ]
    random_question = random.choice(questions)
    correct_answer = random_question["answer"]

    if user_answer.lower() == correct_answer.lower():
        users_collection.update_one({"_id": user_id}, {"$inc": {"score": 1}}, upsert=True)
        return jsonify({"result": "Correct!", "score": users_collection.find_one({"_id": user_id})['score']})
    else:
        return jsonify({"result": "Incorrect!", "score": users_collection.find_one({"_id": user_id})['score']})
