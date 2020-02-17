# DrowningWarning-viz
### Run the app

- From /app

        sudo docker build --tag dw-app .
        sudo docker run --name dw-app -p 5001:5001 dw-app

- Visit http://0.0.0.0:5001/data-input
- Upload the measurement file (csv frmat with .txt or .csv extension)
- Upload the telespor data export for the boat
- Enter the starting time of the box recording
- If you do not know the signal start and signal end timestamps, just enter starttime + 1 sec for signalstart and your estimated end of recording for signalend
- Submitting the form triggers a data processing script that cleans and joins the two datasets and it takes __several seconds__ to finish.
- Choose the parameter(s) you want to show on the map from the top right corner
