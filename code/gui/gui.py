from flask import Flask, render_template_string
from flask_socketio import SocketIO, emit
import threading
import socket
import time
import webbrowser

app = Flask(__name__, static_url_path='/static')
socketio = SocketIO(app)

def broadcast_loop():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    msg = b"ARAC_KONTROL_SUNUCU"
    while True:
        sock.sendto(msg, ("<broadcast>", 54545))
        time.sleep(1)


HTML = """
<!doctype html>
<html>
<head>
    <title>Araç Durumu</title>
    <script src="https://cdn.socket.io/4.0.0/socket.io.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body { font-family: sans-serif; padding: 40px; background: #eef; text-align: center; position: relative; }
        .box {
            background: white;
            padding: 20px;
            margin: auto;
            width: 80%;
            border-radius: 10px;
            box-shadow: 0 0  10px gray;
            transition: transform 0.3s ease, background-color 1s ease;
        }
        .box.updated { background-color: #fffae6; transform: scale(1.02); }
        .row { margin: 10px 0; font-size: 1.2em; }
        .label { font-weight: bold; color: #333; }
        .value { color: #0066cc; }
        table { margin: auto; border-collapse: collapse; width: 90%; margin-top: 20px; }
        th, td { padding: 10px; border: 1px solid #ccc; }
        th { background: #ddd; }

        #clearBtn {
            margin-top: 10px;
            padding: 8px 16px;
            font-size: 1em;
            background-color: #d9534f;
            color: white;
            border: none;
            border-radius: 5px;
        }

        #tobbLogo {
            position: fixed;
            top: 20px;
            left: 20px;
            width: 140px;
            height: 140px;
            height: auto;
            z-index: 1000;
        }

        #directionIcon {
            position: fixed;
            bottom: 50px;
            right: 30px;
            width: 150px;
            height: 150px;
            background-image: url('/static/steering.png');
            background-size: contain;
            background-repeat: no-repeat;
            transition: transform 0.5s ease;
        }

        #startButtonContainer {
            position: fixed;
            bottom: 200px;
            right: 30px; /* direksiyonun sağa olan uzaklığı + buton aralığı */
            width: 150px;
            height: 150px;
        }

        #startButton {
            width: 150px;
            height: 150px;
            object-fit: contain;
            cursor: pointer;
            transition: transform 0.2s ease;
        }


        #startButton:hover {
            transform: scale(1.2);
        }

        #vites {
            position: fixed;
            bottom: 380px;
            right: 70px;
            font-size: 2em;
            font-weight: bold;
            background: white;
            border: 2px solid #ccc;
            border-radius: 8px;
            padding: 10px 20px;
            box-shadow: 0 0 10px rgba(0,0,0,0.2);
        }


        td:nth-child(2) {
            max-width: 150px;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
        }
    </style>
</head>
<body>

    <img src="/static/tobb_logo.png" alt="TOBB ETÜ" id="tobbLogo">


    <div class="box" id="durumBox">
        <h2>🚗 Araçtan Gelen Durum</h2>
        <div class="row"><span class="label">Hareket:</span> <span class="value" id="hareket">...</span></div>
        <div class="row"><span class="label">Şifre:</span> <span class="value" id="sifre">...</span></div>
        <div class="row"><span class="label">Zaman:</span> <span class="value" id="zaman">...</span></div>
    </div>

    <div id="vites">P</div>

    <div class="box">
        <h2>📋 Geçmiş Komutlar</h2>
        <button id="clearBtn" onclick="clearHistory()">🗑️ Geçmişi Temizle</button>
        <table>
            <thead>
                <tr><th>Zaman</th><th>Kişi</th><th>Komut Metni</th><th>Hareket</th><th>Şifre</th></tr>
            </thead>
            <tbody id="history_table"></tbody>
        </table>
    </div>

    <div id="directionIcon"></div>

    <div id="startButtonContainer">
        <img src="/static/startstop_red.png" alt="Start Stop Button" id="startButton" onclick="gonderKomut()">
    </div>


    

<script>
    var socket = io();
    let vitesDurumu = 'P';  // ilk başta P
    let motorCalisiyor = false; // başta kapalı

    function gonderKomut() {
        const button = document.getElementById('startButton');

        if (!motorCalisiyor) {
            motorCalisiyor = true;
            button.src = "/static/startstop_green.png"; 
            console.log("Motor çalıştı");

            const komut = {
                hareket: "motor",
                sure: 2
            };
            socket.emit('komut_gonder', komut);
            updateVites(komut.hareket);
        } else {
            motorCalisiyor = false;
            button.src = "/static/startstop_red.png"; 
            console.log("Motor durdu");
            vitesDurumu = 'P';
            document.getElementById('vites').innerText = vitesDurumu;

            const komut = {
                hareket: "kapat",
                sure: 2
            };
            socket.emit('komut_gonder', komut);
        }
    }



    function updateVites(hareket) {
        hareket = (hareket || '').toLowerCase();

        if (!motorCalisiyor) {
            vitesDurumu = 'P';
        }
        else if (hareket.includes('geri')) {
            vitesDurumu = 'R';
        }
        else if (hareket.includes('git') || hareket.includes('kurtul') ||hareket.includes('ileri') || hareket.includes('sağa') || hareket.includes('sola') ){
            vitesDurumu = 'D';
        }
        else if (hareket.includes('motor') ||hareket.includes('dur') || hareket.includes('komut') ) {
            vitesDurumu = 'N';
        }
        else {
            vitesDurumu = 'N';
        }         
        document.getElementById('vites').innerText = vitesDurumu;
    }


    function updateDirectionIndicator(hareket) {
        const icon = document.getElementById('directionIcon');
        hareket = hareket.toLowerCase();
        if (hareket.includes('sağa')) icon.style.transform = 'rotate(45deg)';
        else if (hareket.includes('sola')) icon.style.transform = 'rotate(-45deg)';
        else icon.style.transform = 'rotate(0deg)';
    }

    function updateTableFromStorage() {
        const table = document.getElementById("history_table");
        const storedData = JSON.parse(localStorage.getItem("komut_gecmisi")) || [];
        table.innerHTML = "";
        storedData.slice().reverse().forEach(entry => {
            const row = document.createElement("tr");
            [entry.zaman, entry.kisi, entry.komut_metni, entry.hareket, entry.sifre].forEach(text => {
                const cell = document.createElement("td");
                cell.innerText = text;
                row.appendChild(cell);
            });
            table.appendChild(row);
        });
    }

    function clearHistory() {
        localStorage.removeItem("komut_gecmisi");
        updateTableFromStorage();
    }

    updateTableFromStorage();

    socket.on('durum_gonder', function(data) {
        document.getElementById('hareket').innerText = data.hareket;
        document.getElementById('sifre').innerText = data.sifre;
        document.getElementById('zaman').innerText = new Date(data.zaman * 1000).toLocaleTimeString();

        updateDirectionIndicator(data.hareket || '');
        updateVites(data.hareket || '');

        const formattedTime = new Date(data.zaman * 1000).toLocaleTimeString();
        let history = JSON.parse(localStorage.getItem("komut_gecmisi")) || [];
        history.push({
            zaman: formattedTime,
            kisi: data.kisi || 'Bilinmiyor',
            komut_metni: data.komut_metni || '',
            hareket: data.hareket,
            sifre: data.sifre
        });
        if (history.length > 20) history = history.slice(-20);
        localStorage.setItem("komut_gecmisi", JSON.stringify(history));
        updateTableFromStorage();
    });
</script>
</body>
</html>
"""


@app.route('/')
def index():
    return render_template_string(HTML)

@socketio.on('connect')
def handle_connect():
    print("Bir istemci bağlandı")

@socketio.on('durum_gonder')
def handle_durum(data):
    print("Veri alındı:", data)
    if 'kisi' not in data:
        data['kisi'] = 'Anonim'
    emit('durum_gonder', data, broadcast=True)

@socketio.on('komut_gonder')
def handle_komut_gonder(data):
    print("Raspberry Pi'ye gönderilecek veri:", data)
    emit('komut_gonder', data, broadcast=True)

if __name__ == '__main__':
    # Yayın başlasın
    threading.Thread(target=broadcast_loop, daemon=True).start()
    
    # Otomatik tarayıcı aç
    def open_browser():
        time.sleep(1)
        webbrowser.open_new("http://localhost:5000")
    
    threading.Thread(target=open_browser).start()
    
    # Sunucuyu başlat
    socketio.run(app, host='0.0.0.0', port=5000)

