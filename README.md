Secret Recovery Tool: Find the Hidden Number!
This tool helps you find a secret number that's been split into many pieces, even if some of those pieces are wrong. Think of it like a puzzle where you need a certain number of correct pieces to see the full picture.
Table of Contents
1.	What This Does
2.	Cool Things It Can Do
3.	The Math Behind It (Simplified)
4.	How to Give It Information
5.	How to Make It Work
6.	Examples of How It Works
7.	What Happens if Something Goes Wrong
1. What This Does
Imagine you have a secret number, and you want to share it with a group of people, but you don't want any single person to know the whole secret. So, you break it into several "shares" (like puzzle pieces). You also decide that you need a certain minimum number of these shares to put the secret back together.
This program's job is to take these shares, figure out which ones are correct (because some might be faulty!), and then use the correct ones to reveal the original secret number.
2. Cool Things It Can Do
●	Reads Your Puzzle Pieces: It can read all the information about your shares from a special file called a JSON file.
●	Figures Out Share Values: Each share isn't just a simple number; it's a small math problem (like "add 100 and 200"). This tool automatically solves those math problems to get the actual numbers for each share.
●	Handles HUGE Numbers: Don't worry if your secret or share numbers are super big. This tool can handle them easily.
●	Finds the Right Pieces: It's smart enough to tell the difference between correct shares and wrong ones. It does this by trying out all possible groups of shares and seeing which secret number appears most often.
●	Uses a Smart Math Trick: It uses a special math trick called "Lagrange Interpolation" to put the secret back together from the correct shares.
3. The Math Behind It (Simplified)
Think of the secret as a point on a hidden curve. Each share is another point on that curve. If you have enough correct points (shares), you can draw the curve. Once you have the curve, you can find where it crosses the "start line" (the y-axis, or x=0), and that crossing point is your secret!
The formula it uses looks a bit complicated, but it's just a way to combine the correct share values to find that starting point of the curve.
P(0)=j=0∑k−1yjm=0,m=j∏k−1xj−xm−xm
The program assumes that all the math steps work out nicely with whole numbers, which is usually how these secret-sharing systems are designed.
4. How to Give It Information
You need to create a simple text file, save it with a .json ending (like my_shares.json), and put your share information inside it like this:
{
  "n": <total_number_of_shares>,
  "k": <minimum_shares_needed>,
  "shares": {
    "<share_number_1>": "<math_problem_for_share_1>",
    "<share_number_2>": "<math_problem_for_share_2>",
    // ... and so on for all your shares
  }
}

●	n: This is the total count of all the shares you're giving the program.
●	k: This is the minimum number of correct shares needed to figure out the secret.
●	shares: This part lists all your shares.
○	The numbers in quotes (like "1") are just labels for your shares (their 'x' values).
○	The text in quotes next to them (like "sum(100,200)") is the math problem that gives you the actual value of that share (its 'y' value).
Examples of Math Problems You Can Use:
●	"sum(100,200)" (adds 100 and 200)
●	"multiply(50,5)" (multiplies 50 by 5)
●	"HCF(120, 180)" (finds the highest common factor of 120 and 180)
●	"LCM(10, 15)" (finds the lowest common multiple of 10 and 15)
●	"sum(1000, 2000, 3000)" (adds three numbers)
5. How to Make It Work
1.	Save the Program: Take the Python code (the processor.py file) and save it in a folder on your computer.
2.	Create Your Share File: In the same folder, create your JSON file (e.g., input_shares.json) with your share information, as explained in How to Give It Information.
3.	Open a Command Window: Open your computer's command prompt or terminal.
4.	Go to Your Folder: Use the cd command to go into the folder where you saved your files (e.g., cd MySecretProject).
5.	Run the Program: Type the following command and press Enter:
python processor.py

The program will then show you the secret number right there in the command window. It will also create a couple of example JSON files (input_shares.json and input_shares_large.json) for you to see how it works.
Running in VS Code (A Popular Code Editor)
1.	Open Your Folder: In VS Code, go to File > Open Folder... and pick the folder where you saved processor.py and your JSON file.
2.	Get the Python Helper: If you haven't already, install the "Python" extension from Microsoft in VS Code (you can find it in the Extensions tab, or by pressing Ctrl+Shift+X).
3.	Run It!: Open processor.py in VS Code. Right-click anywhere in the code and choose "Run Python File in Terminal."
6. Examples of How It Works
The program comes with built-in examples that it creates and uses when you run it:
input_shares.json (Example with Some Wrong Shares):
This example shows how the tool can still find the secret even if some shares are incorrect. The real secret here is 210. Shares number 4 and 5 are purposely made wrong.
{
  "n": 5,
  "k": 3,
  "shares": {
    "1": "sum(100,200)",        // Correct: (share 1, value 300)
    "2": "multiply(50,5)",      // Correct: (share 2, value 250)
    "3": "HCF(120, 180)",       // Correct: (share 3, value 60)
    "4": "LCM(10, 15)",         // Wrong: (share 4, value 30) - should be different
    "5": "sum(1000, 2000, 3000)" // Wrong: (share 5, value 6000) - should be different
  }
}

input_shares_large.json (Example with Big Numbers):
This example shows that the tool can handle very large numbers. The secret here is 5. One of the shares is wrong.
{
  "n": 3,
  "k": 2,
  "shares": {
    "10": "sum(20,5)",          // Correct: (share 10, value 25)
    "20": "sum(40,5)",          // Correct: (share 20, value 45)
    "30": "multiply(30,2,2)"    // Wrong: (share 30, value 120) - should be different
  }
}

7. What Happens if Something Goes Wrong
The program tries its best to tell you if there's a problem:
●	File Not Found: If it can't find your JSON file.
●	Bad JSON: If your JSON file isn't formatted correctly (like missing a comma or a quote).
●	Wrong Numbers (n or k): If the n or k values in your JSON are incorrect.
●	Bad Math Problem: If a share's math problem is written incorrectly or uses a function it doesn't understand.
●	Not Enough Good Shares: If there aren't enough correct shares to figure out the secret.
●	No Consistent Secret: In very rare cases, if too many shares are wrong, it might not be able to find a clear secret.
●	Other Problems: It will also try to catch any other unexpected errors and print a message.
