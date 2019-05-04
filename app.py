from flask import Flask, render_template, redirect, jsonify
import pymongo
from flask_pymongo import PyMongo
import mars_scrape

# Create an instance of Flask
app = Flask(__name__)

# Use PyMongo to establish Mongo connection
mongo = PyMongo(app, uri="mongodb://localhost:27017/mars_data")

@app.route("/")
def index():
        mars_data1 = mongo.db.mars.find_one()
        return render_template('index.html', mars_data=mars_data1)

@app.route("/scrape")
def scraped():
    
    mars_data_scrape = mars_scrape.scrape_info()
    
    mongo.db.mars.update({},mars_data_scrape,upsert=True)
    
    return redirect("http://localhost:5000/", code=302)

if __name__ == "__main__":
    app.run(debug=False)
