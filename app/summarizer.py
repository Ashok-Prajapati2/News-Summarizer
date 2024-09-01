from transformers import pipeline

# Load the summarization pipeline
summarizer = pipeline("summarization")

def summarize_articles(articles):
    summarized_articles = []
    for article in articles:
        try:
            summary = summarizer(article['summary'], max_length=50, min_length=25, do_sample=False)[0]['summary_text']
        except Exception as e:
            summary = article['summary']  # Fallback to the original summary if summarization fails
        summarized_articles.append({
            'title': article['title'],
            'link': article['link'],
            'summary': summary
        })
    return summarized_articles
