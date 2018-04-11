# User manual

This manual contains the instructions for testing MM802 assignment question 2

**Author:** Chenrui Lei (chenrui@aualberta.ca)



## How to test the Question 2

*Note:* pyQt5 and python3 are required in this implementation

1. Open a terminal and open two terminals.
2. Direct to this folder in bother terminals.
3. Using the following command to execute ServerApp.

   ```
   python3 serverGUI.py
   ```

4. Using the following command in another terminal to execute ClientApp.

   ```
   python3 clientGUI.py
   ```

5. Fill in the hostname in both ServerApp and ClientApp.
6. Click the "Establish" button on ServerApp to establish the server.
7. Fill in the image path in ClientApp and click "Send" button to send the image.
8. Click the "Receive" button on server to receive the image and display.
9. You can save the received image from ServerApp if you type in the name of image you would like to save.
10. You can adjust the L value by using the slider in ClientApp and repeat the step 7.

