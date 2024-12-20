
        <h1>Instagram Media Downloader & Uploader</h1>
        <p>This project allows you to download posts from Instagram, extract descriptions, and then upload the media to a Telegram channel and an Eitaa channel.</p>

    <section>
        <h2>Requirements</h2>
        <p>Before using this project, you need to set up your environment properly.</p>
        <ul>
            <li>Install required Python libraries:</li>
        </ul>
        <pre><code>pip install -r requirements.txt</code></pre>
        <ul>
            <li>Install <strong>ChromeDriver</strong> to work with <strong>Selenium</strong>.</li>
        </ul>
    </section>

    <section>
        <h2>Environment Setup</h2>
        <p>This project uses a <code>.env</code> file to store environment variables. To set it up:</p>
        <ol>
            <li>Copy the <code>.env.example</code> file and rename it to <code>.env</code>.</li>
            <li>Fill in the required values in the <code>.env</code> file.</li>
        </ol>

        <h3>Example .env File</h3>
        <pre><code>
BOT_TOKEN_TELEGRAM=your_telegram_bot_token
CHANNEL_TELEGRAM_USERNAME=your_telegram_channel_username
USER_DATA_DIRS=/path/to/your/chrome/user/data
USERNAME_INSTAGRAM_FOR_DOWNLOADS_POSTS=your_instagram_username
EITAA_CHANNEL_USERNAME=your_etaa_channel_username
COMPRESSION=true  # or false
        </code></pre>

        <h3>Environment Variables Explanation:</h3>
        <ul>
            <li><strong>BOT_TOKEN_TELEGRAM:</strong> Your Telegram bot token. (Create a bot with <a href="https://core.telegram.org/bots#botfather" target="_blank">BotFather</a>)</li>
            <li><strong>CHANNEL_TELEGRAM_USERNAME:</strong> Your Telegram channel username to upload the posts.</li>
            <li><strong>USER_DATA_DIRS:</strong> Path to your Chrome user data directory (for Selenium to use your existing Chrome session).</li>
            <li><strong>USERNAME_INSTAGRAM_FOR_DOWNLOADS_POSTS:</strong> Your Instagram username to download posts from.</li>
            <li><strong>EITAA_CHANNEL_USERNAME:</strong> Your Eitaa channel username to upload media to.</li>
            <li><strong>COMPRESSION:</strong> Whether to enable compression for media uploads on Eitaa. Set it to <code>true</code> or <code>false</code>.</li>
        </ul>
    </section>

    <section>
        <h2>Usage</h2>
        <p>Once you have configured your <code>.env</code> file, you can run the script by executing the following command:</p>
        <pre><code>python main.py</code></pre>
        <p>The script will automatically download the latest posts from your Instagram profile and upload them to your Telegram and Eitaa channels.</p>
    </section>

    <section>
        <h2>Project Structure</h2>
        <pre><code>
/project
  ├── main.py                # Main script
  ├── requirements.txt       # Python dependencies
  ├── .env.example           # Example environment variables file
  ├── downloads              # Folder for downloaded media
  └── README.html            # This HTML file
        </code></pre>
    </section>

    <section>
        <h2>Notes</h2>
        <ul>
            <li>Ensure that you run the script in an environment with proper internet access and the required resources (such as Chrome in headless mode for Selenium).</li>
            <li>If you enable compression, please be aware that some formats like videos might lose quality.</li>
        </ul>
    </section>

    <section>
        <h2>Contributing</h2>
        <p>If you have any suggestions or issues, feel free to open an issue or submit a pull request. We welcome contributions!</p>
    </section>
</body>
</html>

<br>
<br>
<br>
<br>
  <p style="color:red;"><p>This code is currently in the testing phase and is not recommended for use in real projects</p></p>

