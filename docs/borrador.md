Borrador funcional?
===================
* Configuración está guardada en base de datos
    +Configuracion global para todas las URLs (timeout,destinatario,template email, etc)
    +Las URLs pertenecen a un sitio/negocio y cada negocio puede tener parámetros defaults propios.
    +Cada URL hereda los parametros default, o del negocio o puede tener los propios.
    +Grupos de usuarios que deben recibir la alerta.
* El loader levanta toda la configuración y se la pasa al orquestador.
    +Urls
    +workers
    +Grupos de usuarios
    +etc
* El orquestador ordena chequeos a los workers de manera asincrónica.
    +El orquestador pública eventos con el resultado del chequeo de acuerdo a la lógica de cada URL (ERROR, OK, WARN,etc…)
* Los workers son procesos independientes que pueden estar en diferentes redes y se comunican con el orquestador por http.
* Mailer se suscribe a los eventos del orquestador  y envía notificaciones por mail de los eventos de acuerdo a la lógica de cada URL.
* Persitidor se suscribe a los eventos del orquestador y los persiste en una base de datos para consultas históricas.
* WS REST/JSON para consulta de estados. Este WS está suscripto a los eventos del “orquestador”  para los datos actuales y levanta datos de la base para consultas históricas.

* Parámetros de una URL
    +id
    +url
    +id_site
    +status
    +last_check_ok
    +last_check_error
    +last_check_warn
    +no_cache (agrega un timestamp al final de la url)
    +mail_subject
    +mail_body
    +hostname
    +timeout
    +SLA
    +destinatarios
    +texto a buscar NO deseado
    +texto a buscar SI deseado
