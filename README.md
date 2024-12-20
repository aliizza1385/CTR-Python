<h1>Instagram Media Downloader & Uploader</h1>
<p>This project allows you to download posts from Instagram, extract descriptions, and then upload the media to a Telegram channel and an Eitaa channel.</p>

<h2>Using Docker</h2>
<p>This project supports Docker for easy setup and deployment. To run the project using Docker, follow these steps:</p>

<ol>
    <li>Make sure you have <strong>Docker</strong> and <strong>Docker Compose</strong> installed. You can follow the installation instructions here:
        <ul>
            <li><a href="https://docs.docker.com/get-docker/" target="_blank">Install Docker</a></li>
            <li><a href="https://docs.docker.com/compose/install/" target="_blank">Install Docker Compose</a></li>
        </ul>
    </li>
    <li>Clone the project repository:</li>
    <pre><code>git clone https://github.com/aliizza1385/CTR-Python.git</code></pre>
    <li>Navigate to the project directory:</li>
    <pre><code>cd CTR-Python</code></pre>
    <li>Create a copy of the example environment file and rename it to <code>.env</code>:</li>
    <pre><code>cp .env.example .env</code></pre>
    <li>Fill in the necessary values in the <code>.env</code> file (e.g., your Telegram bot token, Instagram username, etc.).</li>
    <li>Run the following command to build and start the Docker containers:</li>
    <pre><code>docker-compose up --build</code></pre>
    <li>This will build the Docker images and start the containers. Once it's finished, the project will be running in a Docker container.</li>
</ol>

<h2>Project Structure</h2>
<pre><code>
/project
  ├── main.py                # Main script
  ├── requirements.txt       # Python dependencies
  ├── .env.example           # Example environment variables file
  ├── docker-compose.yml     # Docker Compose configuration
  ├── downloads              # Folder for downloaded media
  └── README.html            # This HTML file
</code></pre>

<h2>Notes</h2>
<ul>
    <li>Ensure that Docker is running on your system and that you have a stable internet connection.</li>
    <li>If you encounter any issues during the Docker build or runtime, check the container logs for more information.</li>
</ul>

<h2>Contributing</h2>
<p>If you have any suggestions or issues, feel free to open an issue or submit a pull request. We welcome contributions!</p>
