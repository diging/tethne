# from flask import Flask
# from datacollection.views import datacollection
# from graphcollection.views import graphcollection
# 
# app = Flask(__name__)
# app.register_blueprint(datacollection, url_prefix='/datacollection')
# app.register_blueprint(graphcollection, url_prefix='/graphcollection')
# 
# print app.url_map
# 
# app.run()



from flask import Flask
from admin.views import admin
from main.views import main

app = Flask(__name__)
app.register_blueprint(admin, url_prefix='/admin')
app.register_blueprint(main, url_prefix='/main')

print app.url_map

app.run()
