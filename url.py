class url:
    """Clase url, para manejar cada url"""
    OK = 0
    NEVER_CHECK = -1
    WARNING = 1
    ERROR = 2
    Status = (
        (OK, 'Chequeo sin problemas '),
        (NEVER_CHECK, 'Primer chequeo no realizado'),
        (WARNING, 'Hubo un problema: en analisis'),
        (ERROR, 'Error en chequeo'),
    )

    def __init__(self, url, hostname, nombre_negocio, url_dinamica, texto_deseado, texto_no_deseado, timeout,  negocio, mail_list, mail_body):
        self.url = url
        self.hsotname = hostname
        self.nombre_negocio = nombre_negocio
        self.url_dinamica = url_dinamica
        self.texto_no_deseado = texto_no_deseado
        self.texto_deseado = texto_deseado
        self.timeout = timeout
        self.negocio = negocio
        self.mail_list = mail_list
        self.mail_body = mail_body
        # inicializados antes del primer chequeo.
        self.status = models.IntegerField(choices=Status, default=NEVER_CHECK)
        self.last_status_text = ''
        self.last_check = '1970-01-01'
        self.last_change_status = '1970-01-01'

    def check_url():
        pass
    


    
