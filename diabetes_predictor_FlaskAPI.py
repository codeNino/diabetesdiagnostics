import joblib
import numpy as np
import warnings
warnings.filterwarnings('ignore')


def Predictor(data):

    model = joblib.load("diabetes_predictor2.pkl")
    model2 = joblib.load("diabetes_predictor3.pkl")

    if data["Glucose"] is None and data["Blood Pressure"] is None:


        pregnancies = data['Pregnancy']
        bmi = data['BMI']
        age = data['Age']
        
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

                
           
        return  {'pred': prediction_output()}
            
        
    else:

        pregnancies = data['Pregnancy']
        glucose = data['Glucose']
        bloodpressure = data['Blood Pressure']
        age = data['Age']
        bmi = data['BMI']

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

           
        return {'pred': prediction_output()}
        