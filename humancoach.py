from flask import Flask, render_template_string, request, Response
import ollama
import sys
import json

app = Flask(__name__)

SYSTEM_PROMPT = """You are a management coach who specializes in small businesses and mentoring leaders to become better leaders. You believe firmly that knowledge workers require leadership as opposed to management; where the role of management is to control a group or group of individuals in order to achieve a specified objective. Leadership is the ability of an individual to influence, motivate, and enable others to contribute to the organization's success.

You are a firm believer in leadership as practice: The practice approach to leadership has been formally developed through a movement called, leadership-as-practice or L-A-P. Its underlying belief is that leadership occurs as a practice rather than reside in the traits or behaviors of individuals.

From now on, can you please answer all questions as this persona? Keep your answers concise and to the point and very short. Keep it professional."""

@app.route('/', methods=['GET'])
def home():
    html = '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Leadership Coach AI</title>
        <style>
            body { 
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
                max-width: 800px;
                margin: 0 auto;
                padding: 20px;
                background-color: #1a1a1a;
                color: #ffffff;
            }
            #response {
                white-space: pre-wrap;
                border: 1px solid #333;
                border-radius: 6px;
                padding: 16px;
                margin-top: 20px;
                min-height: 100px;
                background-color: #2d2d2d;
            }
            textarea {
                width: 100%;
                height: 120px;
                margin-bottom: 16px;
                padding: 12px;
                background-color: #2d2d2d;
                border: 1px solid #333;
                border-radius: 6px;
                color: #ffffff;
                font-size: 14px;
                resize: vertical;
            }
            textarea::placeholder {
                color: #888;
            }
            button {
                padding: 8px 16px;
                background-color: #0066cc;
                color: white;
                border: none;
                border-radius: 4px;
                cursor: pointer;
                font-size: 14px;
                font-weight: 500;
            }
            button:hover {
                background-color: #0052a3;
            }
            button:disabled {
                background-color: #333;
                cursor: not-allowed;
            }
            .error {
                color: #ff4444;
                margin-top: 10px;
                padding: 8px;
                background-color: rgba(255, 68, 68, 0.1);
                border-radius: 4px;
            }
            h1 {
                font-size: 24px;
                font-weight: 500;
                margin-bottom: 24px;
                color: #ffffff;
            }
        </style>
    </head>
    <body>
        <h1>Leadership Coach AI</h1>
        <textarea id="question" placeholder="Ask your leadership question here..."></textarea>
        <br>
        <button onclick="askQuestion()" id="askButton">Ask Question</button>
        <div id="response"></div>

        <script>
            async function askQuestion() {
                const question = document.getElementById('question').value;
                const response = document.getElementById('response');
                const button = document.getElementById('askButton');
                
                if (!question.trim()) {
                    response.textContent = 'Please enter a question';
                    return;
                }
                
                button.disabled = true;
                response.textContent = 'Thinking...';
                
                try {
                    const resp = await fetch('/ask', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({question: question})
                    });

                    if (!resp.ok) {
                        throw new Error(`HTTP error! status: ${resp.status}`);
                    }

                    const reader = resp.body.getReader();
                    const decoder = new TextDecoder();
                    
                    while (true) {
                        const {value, done} = await reader.read();
                        if (done) break;
                        
                        const text = decoder.decode(value);
                        response.textContent += text;
                    }

                } catch (error) {
                    console.error('Error:', error);
                    response.innerHTML = `<div class="error">Error: ${error.message}</div>`;
                } finally {
                    button.disabled = false;
                }
            }
        </script>
    </body>
    </html>
    '''
    return render_template_string(html)

@app.route('/ask', methods=['POST'])
def ask():
    try:
        question = request.json['question']
        
        def generate():
            response = ollama.chat(
                model='llama2:latest',  # Using latest version
                messages=[
                    {
                        'role': 'system',
                        'content': SYSTEM_PROMPT
                    },
                    {
                        'role': 'user',
                        'content': question
                    }
                ]
            )
            
            if response and 'message' in response and 'content' in response['message']:
                return Response(response['message']['content'], mimetype='text/plain')
            else:
                return Response('Error: Invalid response format from Ollama', mimetype='text/plain')
                
        return generate()
            
    except Exception as e:
        print(f"Error in ask route: {str(e)}", file=sys.stderr)
        return Response(f"Error: {str(e)}", mimetype='text/plain')

if __name__ == '__main__':
    app.run(debug=True, port=5000)
