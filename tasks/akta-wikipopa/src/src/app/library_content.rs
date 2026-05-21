use yew::prelude::*;
use stylist::style;

#[component]
pub fn LibraryContent() -> Html {
    let style = style!(
        r#"
            & {
                display: flex;
                max-width: 900px;
                margin: 60px auto;
                font-family: 'Georgia', serif;
                gap: 80px; /* Increased gap for better breathing room */
                padding: 0 40px;
                color: #162e51;
            }

            /* Sidebar */
            .sidebar {
                width: 220px;
                flex-shrink: 0;
            }

            .sidebar-title {
                font-size: 1.5rem;
                font-weight: 700;
                margin-bottom: 8px;
                line-height: 1.2;
                color: #162e51;
            }

            /* Sidebar Navigation */
            .sidebar-nav {
                margin-top: 20px;
                display: flex;
                flex-direction: column;
                gap: 12px;
            }

            .nav-link {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                color: #006699;
                text-decoration: none;
                font-size: 1.05rem;
                font-weight: 400;
                width: fit-content;
            }

            .nav-link:hover {
                text-decoration: underline;
            }

            /* Content Area */
            .main-content {
                flex: 1;
            }

            .main-title {
                font-size: 2.4rem;
                font-weight: 700;
                margin: 0 0 12px 0;
                letter-spacing: -0.5px;
            }

            /* The Double Gold Accent Line */
            .gold-lines {
                margin-bottom: 30px;
            }
            .gold-line {
                height: 2px;
                background-color: #ffbe2e;
                width: 50px;
                margin-bottom: 4px;
            }

            /* File List */
            .file-list {
                list-style-type: none; /* Changed to cleaner list style */
                padding: 0;
                margin-top: 20px;
            }
            .file-item {
                margin-bottom: 12px;
                padding-left: 0;
            }
            .file-link {
                color: #006699;
                text-decoration: none;
                font-family: 'Segoe UI', sans-serif;
                font-size: 1.05rem;
                border-bottom: 1px solid transparent;
                transition: border-color 0.2s;
            }
            .file-link:hover {
                border-bottom: 1px solid #006699;
            }

            @media (max-width: 850px) {
                & {
                    flex-direction: column;
                    gap: 40px;
                    margin: 30px auto;
                    padding: 0 25px;
                }
                .sidebar {
                    width: 100%;
                    border-bottom: 1px solid #eee;
                    padding-bottom: 20px;
                }
                .main-title {
                    font-size: 1.8rem;
                }
            }
        "#
    ).expect("Failed to mount Library styles");

    let files = vec![
        "WPA000001.pdf",
        "WPA000002.pdf",
        "WPA000003.pdf",
        "WPA000004.pdf",
        "WPA000005.pdf",
        "WPA000006.pdf",
    ];

    html! {
        <div class={style}>
            <aside class="sidebar">
                <div class="sidebar-title">{"Wiktor Popiołek library"}</div>
                <div class="gold-lines">
                    <div class="gold-line"></div>
                    <div class="gold-line"></div>
                </div>

                <nav class="sidebar-nav">
                    <a href="/static/ThePrawo.pdf" download="ThePrawo.pdf" class="nav-link">{"The Prawo"}</a>
                    <a href="/static/WielkiBrat.zip" download="WielkiBrat.zip" class="nav-link">{"Program do ustalania kar"}</a>
                </nav>
            </aside>

            <main class="main-content">
                <h1 class="main-title">{"Data Set Files"}</h1>
                <div class="gold-lines">
                    <div class="gold-line"></div>
                    <div class="gold-line"></div>
                </div>

                <ul class="file-list">
                    {for files.into_iter().map(|file| {
                        let path = format!("/static/{}", file); // Path points to your static folder
                        let filename = file.to_string();
                        html! {
                            <li class="file-item">
                                <a
                                    href={path}
                                    class="file-link"
                                    download={filename}
                                >
                                    {file}
                                </a>
                            </li>
                        }
                    })}
                </ul>
            </main>
        </div>
    }
}