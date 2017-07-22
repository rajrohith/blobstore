from app import app
import os

port = int(os.getenv("PORT", 443))
app.run(host='0.0.0.0', port=port)
