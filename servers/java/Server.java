import java.io.InputStream;
import java.io.OutputStream;
import java.net.InetSocketAddress;
import java.net.ServerSocket;
import java.net.Socket;

public class Server {
    private static final int PORT = 8081;
    private static final int BACKLOG = 4096;
    private static final int BUFFER_SIZE = 4096;

    public static void main(String[] args) throws Exception {

        /*
         * HTTP response
         *
         * Keep this the same as the other servers so that
         * we are actually testing the same workload.
         */
        String response =
                "HTTP/1.1 200 OK\r\n" +
                "Content-Type: text/plain\r\n" +
                "Content-Length: 13\r\n" +
                "Connection: close\r\n" +
                "\r\n" +
                "Hello World!\n";

        byte[] responseBytes = response.getBytes("UTF-8");

        // Creating the server socket
        ServerSocket server = new ServerSocket();

        /*
         * Allow the address to be reused after restarting
         * the server.
         */
        server.setReuseAddress(true);

        // Bind the socket to the address and port
        server.bind(new InetSocketAddress("0.0.0.0", PORT),BACKLOG);

        System.out.println("Java server listening on port " + PORT);

        while (true) {

            // Accept an incoming connection
            Socket client = server.accept();

            try {

                /*
                 * Disable Nagle's algorithm.
                 *
                 * The response is tiny, so we don't want
                 * TCP adding its small-packet delay here.
                 */
                client.setTcpNoDelay(true);

                // Get the input and output streams
                InputStream input = client.getInputStream();
                OutputStream output = client.getOutputStream();

                // Buffer for the HTTP request
                byte[] buffer = new byte[BUFFER_SIZE];

                // Read the HTTP request
                int bytesRead = input.read(buffer);

                if (bytesRead > 0) {

                    // Send the fixed HTTP response
                    output.write(responseBytes);
                    output.flush();
                }

            } catch (Exception ignored) {

                /*
                 * The client may disconnect before we finish
                 * sending the response.
                 *
                 * Ignore that for the benchmark.
                 */

            } finally {
                // Close the connection after one request
                client.close();
            }
        }
    }
}