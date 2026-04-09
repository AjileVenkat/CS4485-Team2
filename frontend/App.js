import axios from 'axios';

const handleFileUpload = async (event) => {
    const file = event.target.files[0];
    const formData = new FormData();
    formData.append('file', file)

    try{
        const response = await axios.post('http://127.0.0.1:8000/predict', formData, {
            headers: { 'Content-Type': 'multipart/form-data' }
        });
        console.log("Prediction: ", response.data.prediction);
        console.log("Risk Score: ", response.data.risk_score);
    } catch (error){
        console.error("Analysis failed", error);
    }
}