use yew::prelude::*;
use stylist::style;

#[component]
pub fn Navbar() -> Html {
    let navbar_style = style!(
        r#"
            & {
                min-width: 100%;
                background-color: #162e51;
                font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
                box-shadow: 0 4px 12px rgba(0,0,0,0.1);
            }
            .navbar-container {
                max-width: 900px;
                margin: 0 auto;
                display: flex;
                align-items: center;
                justify-content: space-between;
                padding: 1.25rem 2rem;
            }
            .navbar-brand {
                display: flex;
                align-items: center;
                transition: transform 0.2s ease;
            }

            .seal {
                height: 6.7rem;
                width: auto;
                filter: drop-shadow(0 2px 4px rgba(0,0,0,0.2));
            }

            .law-button {
                display: inline-block;
                background: linear-gradient(180deg, #ffce5a 0%, #ffbe2e 100%);
                color: #162e51;
                text-decoration: none;
                font-size: 1.1rem;
                font-weight: 700;
                text-transform: uppercase;
                letter-spacing: 1.5px;
                padding: 1rem 3rem;
                border-radius: 4px;
                border: none;
                box-shadow:
                    0 4px 0px #b3861f,
                    0 6px 15px rgba(0,0,0.3);
                transition: all 0.15s ease-in-out;
                position: relative;
                top: 0;
            }

            .law-button:hover {
                background: linear-gradient(180deg, #ffd670 0%, #ffc445 100%);
                transform: translateY(-2px);
                box-shadow:
                    0 6px 0px #b3861f,
                    0 8px 20px rgba(0,0,0,0.4);
            }

            .law-button:active {
                transform: translateY(2px);
                box-shadow:
                    0 2px 0px #b3861f,
                    0 4px 10px rgba(0,0,0,0.3);
            }

            .black-bar {
                background-color: #2e2e2a;
                border-top: 3px solid #ffbe2e;
                height: 70px;
                width: 100%;
                display: flex;
                align-items: center;
                justify-content: center;
            }
            .black-bar span {
                color: #ffffff;
                font-size: 1rem;
                letter-spacing: 3px;
                text-transform: uppercase;
                font-weight: 600;
                opacity: 0.9;
            }

            @media (max-width: 768px) {
                .navbar-container {
                    flex-direction: column;
                    padding: 1.5rem 1rem;
                    gap: 1.5rem;
                }
                .law-button {
                    width: 100%;
                    text-align: center;
                    padding: 1rem 0;
                }
            }
        "#
    )
        .expect("Failed to mount DOJ navbar styles");

    html! {
        <div class={classes!(navbar_style)} >
            <nav aria-label="Main navigation">
                <div class="navbar-container">
                    <div class="navbar-brand">
                        <img
                            class="seal"
                            src="static/logo.png"
                            alt="logo"
                        />
                    </div>

                    <a href="/static/ThePrawo.pdf" download="ThePrawo.pdf" class="law-button">
                        {"The Prawo"}
                    </a>
                </div>
            </nav>
            <div class="black-bar">
                <span>{"SZYPKIE MINISTERSTWO SPRAWIEDLIWOŚCI"}</span>
            </div>
        </div>
    }
}