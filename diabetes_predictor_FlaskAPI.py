import flask.scaffold
flask.helpers._endpoint_from_view_func = flask.scaffold._endpoint_from_view_func
from flask import Flask, jsonify, request
from flask_restful import Api, Resource
import joblib
import numpy as np
import warnings
warnings.filterwarnings('ignore')


app = Flask(__name__)
api = Api(app)


model = joblib.load("diabetes_predictor2.pkl")
model2 = joblib.load("diabetes_predictor3.pkl")


class Detect(Resource):
    
    def post(self):

        postedData= request.get_json()

        if postedData["Glucose"] is None and postedData["Blood Pressure"] is None:


            pregnancies = postedData['Pregnancy']
            bmi = postedData['BMI']
            age = postedData['Age']
        
            user_data = [int(pregnancies),
                         float(bmi),
                       int(age)]

            user_input = np.array(user_data)

               
            prediction = model2.predict(user_input.reshape(1,-1))[0]
            confidence = model2.predict_proba(user_input.reshape(1,-1))[0]            
                
            
            def prediction_output(pred=prediction, confidence=confidence):
    
                if pred == 0:

                    return f"your health data sugggests that you are non diabetic but at {100 - int(round(confidence[0]*100,0))}% risk."
    
                else:

                    return f"your health data suggests that you are diabetic with a {round(confidence[1]*100,1)}% predictive confidence."

                
           
            return  jsonify({'pred': prediction_output()})
            
        
        else:

            pregnancies = postedData['Pregnancy']
            glucose = postedData['Glucose']
            bloodpressure = postedData['Blood Pressure']
            age = postedData['Age']
            bmi = postedData['BMI']

            user_data =   [ int(pregnancies),
                         float(glucose),
                float(bloodpressure),
                float(bmi),
                       int(age) ]

            
            user_input = np.array(user_data)

            prediction = model.predict(user_input.reshape(1,-1))[0]
            confidence = model.predict_proba(user_input.reshape(1,-1))[0]

            def prediction_output(pred=prediction, confidence=confidence):

                
                if pred == 0:

                    return f"your health data sugggests that you are non diabetic but at {100 - int(round(confidence[0]*100,0))}% risk."
    
                else:

                    return f"your health data suggests that you are diabetic with a {round(confidence[1]*100,1)}% predictive confidence."

           
            return jsonify({'pred': prediction_output()})





          
api.add_resource(Detect, '/detect')

if __name__ == '__main__':
    app.run(host='127.0.0.1', port = 5002, debug=True)
        