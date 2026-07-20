# Aaron-l Portfolio

A personal portfolio website generator and local administration application.

## Features

* Local portfolio management
* Album management
* Artwork management
* Blog/post system
* JSON-based content storage
* Static website generation
* Automatic cleanup of removed content
* Local PySide6 administration interface
* Automatic Git publishing
* GitHub Pages deployment

## Technologies

* Python
* PySide6
* HTML
* CSS
* JSON
* Git
* GitHub Actions
* GitHub Pages

## Project Structure

```
Aaron-l Portfolio/

├── admin/
│   ├── data/
│   ├── generator/
│   ├── templates/
│   ├── tools/
│   ├── ui/
│   └── main.py
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

## Running Locally

Start the administration application:

```
cd admin
python main.py
```

Use the application to edit:

* About information
* Albums
* Artwork
* Posts
* Attachments

After making changes:

1. Generate the website
2. Review the generated files
3. Publish changes through Git

## Deployment

The website is deployed using:

* GitHub Pages
* GitHub Actions

The deployed website:

```
https://pixiv-aaron-l.github.io/Aaron-l-Portfolio/
```

## Privacy

Private information must never be committed to this repository.

Examples:

* passwords
* API keys
* private credentials
* personal configuration files

Sensitive files should be excluded using:

```
.gitignore
```

## License

The source code of this project may be reused, modified, and redistributed under these conditions:

* Credit must be given to Aaron-l Portfolio.
* A visible link to the original website must be included when the code is reused publicly.
* Original attribution must not be removed.
* This permission applies only to the source code.

The following are **not included**:

* Artwork
* Images
* Personal content
* Written posts
* Private data

Those remain the property of the original creator.

Original website:

https://pixiv-aaron-l.github.io/Aaron-l-Portfolio/

```
```
