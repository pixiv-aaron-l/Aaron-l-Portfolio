# Aaron-l Portfolio

A personal portfolio website generator and local administration application.

## Features

- Local portfolio management
- Album management
- Artwork management
- Blog/post system
- Attachments on posts, each with **Download** and **View** buttons
- Hosting attachments: put a file on the website without a post, and get a web link for it
- JSON-based content storage
- Static website generation
- Automatic cleanup of removed content
- Local PySide6 administration interface (opens without a console window)
- Automatic Git publishing
- GitHub Pages deployment

## Technologies

- Python
- PySide6
- HTML
- CSS
- JSON
- Git
- GitHub Actions
- GitHub Pages

## Project Structure

```
Aaron-l Portfolio/

├── admin/
│   ├── data/
│   ├── generator/
│   ├── templates/
│   ├── tools/
│   ├── ui/
│   ├── main.py
│   └── main.pyw
│
├── setup/
│   └── Install.bat
│
├── website/
│   ├── images/
│   ├── albums/
│   ├── artworks/
│   ├── posts/
│   ├── attachments/
│   ├── index.html
│   ├── arts.html
│   ├── posts.html
│   ├── view.html
│   └── style.css
│
├── .github/
│   └── workflows/
│       └── deploy.yml
│
├── .gitignore
├── README.md
└── LICENSE
```

## How It Works

The admin application manages website content locally.

Content is stored as JSON files:

```
admin/data/
```

The generator converts this information into a complete static website:

```
website/
```

The generated website is automatically published using Git.

GitHub Actions then deploys the website through GitHub Pages.

## Installing (Windows)

You only need Python and Git on your computer. A small installer sets both up for you.

1. Download or clone this repository.
2. Double-click `setup/Install.bat`.
   It installs Python and Git if they are missing, installs the packages the admin needs, and puts a **website upload** shortcut on your desktop.
   If it has to install Python or Git it will ask you to close the window and run it once more. That is normal.
3. Open **website upload** from your desktop (or double-click `admin/main.pyw`).

### Linking it to your GitHub (first time only)

Publishing needs the project folder to be linked to your own repository.

1. Create an empty repository on GitHub.
2. In the project folder, link it:

```
git remote add origin https://github.com/YOUR-NAME/YOUR-REPOSITORY.git
```

3. In the repository settings on GitHub, open **Pages** and choose **GitHub Actions** as the source.
4. The first time you click **Publish Website**, Git opens a browser window so you can sign in to GitHub.

The admin reads your GitHub name and repository from this link by itself, so there is nothing to type into the code.

### Starting your own site

The code can be reused (see License), but my content cannot. Before you publish, remove everything of mine:
the files inside `website/images`, `website/albums`, `website/artworks`, `website/posts` and `website/attachments`, and the files inside `admin/data`. Then add your own from the admin.

## Running Locally

Open the administration application with the desktop shortcut, or double-click:

```
admin/main.pyw
```

(`main.pyw` opens it without a console window. If you prefer a console, you can still start it with:)

```
cd admin
python main.py
```

Use the application to edit:

- About information
- Albums
- Artwork
- Posts
- Attachments

After making changes:

1. Generate the website
2. Review the generated files
3. Publish changes through Git

## Attachments

Every attachment on a post shows **Download** and **View**.

- **Download** always downloads the file.
- **View** opens the file on a full page with just a **Return** button: text, HTML, PDF and images are shown as they are, a saved web page (`.mht`) is shown as a normal page, and `.zip` / `.7z` show a short summary (size, how many files, what is at the top level; for `.7z` this needs the optional `py7zr` package, which the installer adds).

### Hosting attachments

In the admin, **Dashboard → Hosting Attachments** puts a file on the website without a post. Select it and use **Copy Web Link** to share it anywhere. Hosted files are normal attachments, nothing links to them from the site.

## Deployment

The website is deployed using:

- GitHub Pages
- GitHub Actions

The deployed website:

https://pixiv-aaron-l.github.io/Aaron-l-Portfolio/

## Privacy

Private information must never be committed to this repository.

Examples:

- passwords
- API keys
- private credentials
- personal configuration files

Sensitive files should be excluded using:

```
.gitignore
```

## License

The source code of this project may be reused, modified, and redistributed under these conditions:

1. Credit must be given to Aaron-l Portfolio.
2. A visible link to the original website must be included when the code is reused publicly.
3. Original attribution must not be removed.
4. This permission applies only to the source code.

The following are not included:

- Artwork
- Images
- Personal content
- Written posts
- Private data

Those remain the property of the original creator.

Original website:

https://pixiv-aaron-l.github.io/Aaron-l-Portfolio/
