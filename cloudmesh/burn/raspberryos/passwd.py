import textwrap


class Passwd:
    file = textwrap.dedent("""
        root:x:0:0:root:/root:/bin/bash
        daemon:x:1:1:daemon:/usr/sbin:/usr/sbin/nologin
        bin:x:2:2:bin:/bin:/usr/sbin/nologin
        sys:x:3:3:sys:/dev:/usr/sbin/nologin
        sync:x:4:65534:sync:/bin:/bin/sync
        games:x:5:60:games:/usr/games:/usr/sbin/nologin
        man:x:6:12:man:/var/cache/man:/usr/sbin/nologin
        lp:x:7:7:lp:/var/spool/lpd:/usr/sbin/nologin
        mail:x:8:8:mail:/var/mail:/usr/sbin/nologin
        news:x:9:9:news:/var/spool/news:/usr/sbin/nologin
        uucp:x:10:10:uucp:/var/spool/uucp:/usr/sbin/nologin
        proxy:x:13:13:proxy:/bin:/usr/sbin/nologin
        www-data:x:33:33:www-data:/var/www:/usr/sbin/nologin
        backup:x:34:34:backup:/var/backups:/usr/sbin/nologin
        list:x:38:38:Mailing List Manager:/var/list:/usr/sbin/nologin
        irc:x:39:39:ircd:/var/run/ircd:/usr/sbin/nologin
        gnats:x:41:41:Gnats Bug-Reporting System (admin):/var/lib/gnats:/usr/sbin/nologin
        nobody:x:65534:65534:nobody:/nonexistent:/usr/sbin/nologin
        systemd-timesync:x:100:102:systemd Time Synchronization,,,:/run/systemd:/usr/sbin/nologin
        systemd-network:x:101:103:systemd Network Management,,,:/run/systemd:/usr/sbin/nologin
        systemd-resolve:x:102:104:systemd Resolver,,,:/run/systemd:/usr/sbin/nologin
        _apt:x:103:65534::/nonexistent:/usr/sbin/nologin
        pi:x:1000:1000:,,,:/home/pi:/bin/bash
        messagebus:x:104:110::/nonexistent:/usr/sbin/nologin
        _rpc:x:105:65534::/run/rpcbind:/usr/sbin/nologin
        statd:x:106:65534::/var/lib/nfs:/usr/sbin/nologin
        sshd:x:107:65534::/run/sshd:/usr/sbin/nologin
        avahi:x:108:113:Avahi mDNS daemon,,,:/var/run/avahi-daemon:/usr/sbin/nologin
        lightdm:x:109:114:Light Display Manager:/var/lib/lightdm:/bin/false
        rtkit:x:110:116:RealtimeKit,,,:/proc:/usr/sbin/nologin
        pulse:x:111:119:PulseAudio daemon,,,:/var/run/pulse:/usr/sbin/nologin
        saned:x:112:122::/var/lib/saned:/usr/sbin/nologin
        hplip:x:113:7:HPLIP system user,,,:/var/run/hplip:/bin/false
        colord:x:114:123:colord colour management daemon,,,:/var/lib/colord:/usr/sbin/nologin
        """)

    shadow = textwrap.dedent("""
        root:*:18638:0:99999:7:::
        daemon:*:18638:0:99999:7:::
        bin:*:18638:0:99999:7:::
        sys:*:18638:0:99999:7:::
        sync:*:18638:0:99999:7:::
        games:*:18638:0:99999:7:::
        man:*:18638:0:99999:7:::
        lp:*:18638:0:99999:7:::
        mail:*:18638:0:99999:7:::
        news:*:18638:0:99999:7:::
        uucp:*:18638:0:99999:7:::
        proxy:*:18638:0:99999:7:::
        www-data:*:18638:0:99999:7:::
        backup:*:18638:0:99999:7:::
        list:*:18638:0:99999:7:::
        irc:*:18638:0:99999:7:::
        gnats:*:18638:0:99999:7:::
        nobody:*:18638:0:99999:7:::
        systemd-timesync:*:18638:0:99999:7:::
        systemd-network:*:18638:0:99999:7:::
        systemd-resolve:*:18638:0:99999:7:::
        _apt:*:18638:0:99999:7:::
        pi:$6$ZTD6hJH7f.ZyvE3M$Tgfv.ULQpXRtW7YRxImuFX1qrfVO5BGwTm17w/0.WYBiEck6mE5vRcFfJy.NgrYIJqU.aOGpu//hhYwL1uh8T.:18638:0:99999:7:::
        messagebus:*:18638:0:99999:7:::
        _rpc:*:18638:0:99999:7:::
        statd:*:18638:0:99999:7:::
        sshd:*:18638:0:99999:7:::
        avahi:*:18638:0:99999:7:::
        lightdm:*:18638:0:99999:7:::
        rtkit:*:18638:0:99999:7:::
        pulse:*:18638:0:99999:7:::
        saned:*:18638:0:99999:7:::
        hplip:*:18638:0:99999:7:::
        colord:*:18638:0:99999:7:::
        """)
