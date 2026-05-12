import com.sun.net.httpserver.HttpServer;
import com.sun.net.httpserver.HttpExchange;
import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;

import java.io.IOException;
import java.io.OutputStream;
import java.net.InetSocketAddress;
import java.nio.charset.StandardCharsets;

public class Main {

    private static final Logger logger = LogManager.getLogger(Main.class);

    public static void main(String[] args) throws IOException {

        HttpServer server = HttpServer.create(new InetSocketAddress(80), 0);

        // Strona HTML
        server.createContext("/", exchange -> {
            String html = """
                <html>
                    <body>
                        <h1>Login</h1>
                        <form method="POST" action="/login">
                            <input name="userId" placeholder="User ID"/>
                            <button type="submit">Login</button>
                        </form>
                    </body>
                </html>
            """;

            sendResponse(exchange, html);
        });

        // Login endpoint
        server.createContext("/login", exchange -> {

            if ("POST".equals(exchange.getRequestMethod())) {

                String body = new String(exchange.getRequestBody().readAllBytes());

                String userId = parseUserId(body);

                // LOGOWANIE (format %m %n z configa)
                logger.info("LOGIN userId=" + userId);

                sendResponse(exchange, "Logged user: " + userId);
            } else {
                sendResponse(exchange, "Method not allowed");
            }
        });

        server.start();
        System.out.println("Server running on http://localhost:80");
    }

    private static String parseUserId(String body) {
        // bardzo proste parsowanie: userId=123
        if (body.contains("userId=")) {
            return body.split("userId=")[1];
        }
        return "unknown";
    }

    private static void sendResponse(HttpExchange exchange, String response) throws IOException {
        exchange.sendResponseHeaders(200, response.getBytes(StandardCharsets.UTF_8).length);

        OutputStream os = exchange.getResponseBody();
        os.write(response.getBytes(StandardCharsets.UTF_8));
        os.close();
    }
}