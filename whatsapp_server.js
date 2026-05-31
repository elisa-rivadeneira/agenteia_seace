
const { Client, LocalAuth } = require('whatsapp-web.js');
const qrcode = require('qrcode-terminal');

const client = new Client({
    authStrategy: new LocalAuth()
});

client.on('qr', (qr) => {
    console.log('📱 Escanea este QR code con WhatsApp:');
    qrcode.generate(qr, {small: true});
});

client.on('ready', () => {
    console.log('✅ WhatsApp conectado exitosamente!');
    console.log('🚀 Servidor listo para envío automático');

    // Crear servidor HTTP simple para recibir mensajes
    const http = require('http');

    const server = http.createServer((req, res) => {
        if (req.method === 'POST' && req.url === '/send') {
            let body = '';

            req.on('data', chunk => {
                body += chunk.toString();
            });

            req.on('end', () => {
                try {
                    const data = JSON.parse(body);
                    const { number, message } = data;

                    client.sendMessage(number + '@c.us', message)
                        .then(() => {
                            res.writeHead(200, {'Content-Type': 'application/json'});
                            res.end(JSON.stringify({success: true, message: 'Enviado'}));
                            console.log(`✅ Mensaje enviado a ${number}: ${message.substring(0, 50)}...`);
                        })
                        .catch(err => {
                            res.writeHead(500, {'Content-Type': 'application/json'});
                            res.end(JSON.stringify({success: false, error: err.message}));
                            console.log(`❌ Error enviando: ${err.message}`);
                        });
                } catch (err) {
                    res.writeHead(400, {'Content-Type': 'application/json'});
                    res.end(JSON.stringify({success: false, error: 'JSON inválido'}));
                }
            });
        } else if (req.method === 'GET' && req.url === '/status') {
            res.writeHead(200, {'Content-Type': 'application/json'});
            res.end(JSON.stringify({
                status: 'connected',
                ready: client.info !== null
            }));
        } else {
            res.writeHead(404);
            res.end('Not Found');
        }
    });

    server.listen(3001, () => {
        console.log('🌐 Servidor HTTP corriendo en puerto 3001');
        console.log('📡 Endpoint: POST /send');
        console.log('📊 Status: GET /status');
    });
});

client.on('message', message => {
    // Puedes agregar lógica para responder mensajes aquí
});

client.initialize();
