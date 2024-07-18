from flask import Flask, request, render_template, send_file # type: ignore
import re
import math
import io

app = Flask(__name__)

# Sample database of documents
documents = [
    "database1.txt",  # Placeholder for file names or paths
    "database2.txt",
    "database3.txt"
]

@app.route("/", methods=["GET", "POST"])
def loadPage():
    query = ""
    output = []
    if request.method == "POST":
        query = request.form.get("query", "").strip()
        if "file" in request.files:
            file = request.files["file"]
            if file.filename != "":
                query = file.read().decode("utf-8").strip()
        
        # Perform plagiarism check against the database
        output = check_plagiarism(query)

    return render_template("pla.html", query=query, output=output)

@app.route("/export", methods=["POST"])
def export_results():
    query = request.form.get("query", "").strip()
    output = check_plagiarism(query)

    # Create a text file with the results
    result_text = f"Plagiarism Check Results:\n\n"
    result_text += f"Input Text:\n{query}\n\n"
    for result in output:
        result_text += f"{result}\n"

    # Convert the text to a file-like object
    result_file = io.StringIO(result_text)
    result_file.seek(0)

    return send_file(result_file, as_attachment=True, download_name="plagiarism_results.txt", mimetype='text/plain')

def check_plagiarism(query):
    if not query:
        return ["No text provided for plagiarism check."]
    
    results = []
    for doc in documents:
        with open(doc, "r") as fd:
            database = fd.read().lower()
        similarity = calculate_similarity(query, database)
        results.append(f"Document: {doc} | Similarity: {similarity:.2f}%")
    
    return results

def calculate_similarity(query, database):
    universalSetOfUniqueWords = []
    matchPercentage = 0

    lowercaseQuery = query.lower()
    queryWordList = re.sub(r"[^\w]", " ", lowercaseQuery).split()

    for word in queryWordList:
        if word not in universalSetOfUniqueWords:
            universalSetOfUniqueWords.append(word)

    databaseWordList = re.sub(r"[^\w]", " ", database).split()

    for word in databaseWordList:
        if word not in universalSetOfUniqueWords:
            universalSetOfUniqueWords.append(word)

    queryTF = []
    databaseTF = []

    for word in universalSetOfUniqueWords:
        queryTfCounter = queryWordList.count(word)
        databaseTfCounter = databaseWordList.count(word)
        
        queryTF.append(queryTfCounter)
        databaseTF.append(databaseTfCounter)

    dotProduct = sum(queryTF[i] * databaseTF[i] for i in range(len(queryTF)))

    queryVectorMagnitude = math.sqrt(sum(tf ** 2 for tf in queryTF))
    databaseVectorMagnitude = math.sqrt(sum(tf ** 2 for tf in databaseTF))

    if queryVectorMagnitude == 0 or databaseVectorMagnitude == 0:
        matchPercentage = 0.0
    else:
        matchPercentage = (dotProduct / (queryVectorMagnitude * databaseVectorMagnitude)) * 100

    return matchPercentage

if __name__ == "__main__":
    app.run(debug=True)
