use yew::prelude::*;
use stylist::style;

#[component]
pub fn Footer() -> Html {
    let footer_style = style!(
        r#"
            & {
                width: 100%;
                background-color: #2e2e2a;
                border-top: 3px solid #ffbe2e;
                padding: 1.5rem 0;
                display: flex;
                justify-content: center;
                position: fixed;
                bottom: 0;
                align-items: center;
                font-family: 'Segoe UI', sans-serif;
                margin-top: auto; /* To jest klucz do wypchnięcia na dół */
            }

            .footer-text {
                color: #ffffff;
                font-size: 0.85rem;
                letter-spacing: 1px;
            }

            .yew-link {
                color: #ffbe2e;
                text-decoration: none;
                font-weight: 600;
                margin-left: 5px;
            }

            .yew-link:hover {
                text-decoration: underline;
            }
        "#
    ).expect("Failed to mount footer styles");

    html! {
        <footer class={footer_style}>
            <div class="footer-text">
                {"stworzone z"}
                <a
                    href="https://github.com/yewstack/yew"
                    target="_blank"
                    rel="noopener noreferrer"
                    class="yew-link"
                >
                    {"yew"}
                </a>
            </div>
        </footer>
    }
}