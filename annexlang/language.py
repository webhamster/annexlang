from .components import ProtocolStep

class Request(ProtocolStep):
    yaml_tag = "!request"
    type = "request"
    text = ""
    html_template = """
    {% if not this.html_rtl %}
    <div class="{{ this.type }}" style="grid-column: {{this.src.annexid}} / {{this.dest.annexid}}; grid-row: {{this.line + 1}} / span 1">
    {% else %}
    <div class="{{ this.type }} rtl" style="grid-column: {{this.dest.annexid}} / {{this.src.annexid}}; grid-row: {{this.line + 1}} / span 1">
    {% endif %}
    {{ this.html_id }} {{ this.html_text }} 
    </div>
    """

    def _init(self, *args, **kwargs):
        super()._init(*args, **kwargs)
        if hasattr(self, 'reply_to'):
            self.dest = self.reply_to.src
            self.src = self.reply_to.dest
        self._affecting_nodes = [
            self.get_pos(self.src.column, self.line),
            self.get_pos(self.dest.column, self.line)
        ]

    @property
    def affected_parties(self):
        yield self.src
        yield self.dest

    @property
    def html_rtl(self):  # true if this step needs to be drawn from right to left
        return self.src.column > self.dest.column
    
    @property
    def html_text(self):
        return self.text
        #{{ this.method }} {{ this.url }} {{this.parameters }}
    
    @property
    def height(self):
        if self.tikz_above and self.tikz_below:
            return "4ex" + ("+2ex" * len(self.lines_below)), "north,yshift=3ex"
        elif self.tikz_above:
            return "4ex", "south,yshift=-1ex"
        elif self.tikz_below:
            return "2ex" + ("+2ex" * len(self.lines_below)), "north,yshift=1ex"
        else:
            return "1ex", "center"
    
    def tikz_arrows(self):
        src = self.get_pos(self.src.column, self.line)
        dest = self.get_pos(self.dest.column, self.line)
        return fr"""%% draw {self.type}
        \draw[annex_{self.type}{self.tikz_extra_style}] ({src}) to {self.tikz_above} {self.tikz_below} ({dest});"""

class HTTPRequest(Request):
    yaml_tag = '!http-request'
    method = ""
    url = ""
    parameters = ""
    type = "http_request"
    id_above = True

    def _init(self, *args, **kwargs):
        super()._init(*args, **kwargs)
        self.text_above = " ".join((self.method, self.url, )).strip()
        self.text_below = self.parameters

    @property
    def html_text(self):
        return f'<span class="http_method">{self.method}</span> <span class="http_url">{self.url}</span> <span class="http_parameters">{self.parameters}</span> '



class XHRRequest(HTTPRequest):
    yaml_tag = '!xhr-request'
    type = "xhr_request"


class HTTPResponse(HTTPRequest):
    yaml_tag = '!http-response'
    code = ""
    headers = ""
    type = "http_response"
    
    def _init(self, *args, **kwargs):
        super()._init(*args, **kwargs)
        self.text_above = " ".join((self.code, self.headers, )).strip()
        if not self.text_above and not self.skip_number:
            self.text_above = 'Response'
        self.text_below = self.parameters

    @property
    def html_text(self):
        return f'<span class="http_code">{self.code}</span> <span class="http_headers">{self.headers}</span> '


class XHRResponse(HTTPResponse):
    yaml_tag = '!xhr-response'
    type = "xhr_response"


class Websocket(Request):
    yaml_tag = '!websocket'
    type = "websocket"

    def _init(self, *args, **kwargs):
        super()._init(*args, **kwargs)
        self.text_above = "WebSocket"
        self.text_below = self.parameters
    
    @property
    def html_text(self):
        return f'<span class="websocket_parameters">{self.parameters}</span> '
    

class HTTPRequestResponse(HTTPRequest):
    yaml_tag = '!http-request-response'
    type = "request_response"
    type_above = 'http_request'
    type_below = 'http_response'

    def tikz_arrows(self):
        src = self.get_pos(self.src.column, self.line)
        dest = self.get_pos(self.dest.column, self.line)
        return fr"""%% draw {self.type}
        \draw[annex_{self.type_above},transform canvas={{yshift=0.25ex}}{self.tikz_extra_style}] ({src}) to {self.tikz_above} ({dest});
        \draw[annex_{self.type_below},transform canvas={{yshift=-0.25ex}}{self.tikz_extra_style}] ({dest}) to {self.tikz_below} ({src});"""


class XHRRequestResponse(HTTPRequestResponse):
    yaml_tag = '!xhr-request-response'
    type = "xhr_request_response"
    type_above = 'xhr_request'
    type_below = 'xhr_response'


class HTTPResponseRequest(HTTPRequest):
    yaml_tag = '!http-response-request'
    type = "response_request"
    type_above = 'http_response'
    type_below = 'http_request'

    def tikz_arrows(self):
        src = self.get_pos(self.src.column, self.line)
        dest = self.get_pos(self.dest.column, self.line)
        return fr"""%% draw {self.type}
        \draw[annex_{self.type_above},transform canvas={{yshift=0.25ex}}{self.tikz_extra_style}] ({dest}) to {self.tikz_above} ({src});
        \draw[annex_{self.type_below},transform canvas={{yshift=-0.25ex}}{self.tikz_extra_style}] ({src}) to {self.tikz_below} ({dest});"""

    
class XHRResponseRequest(HTTPResponseRequest):
    yaml_tag = '!xhr-request-response'
    type = "xhr_request_response"
    type_above = 'xhr_request'
    type_below = 'xhr_response'


class PostMessage(Request):
    yaml_tag = '!postmessage'
    body = ""
    comment = ""
    id_above = True
    text_style = "annex_postmessage_text"
    type = "postmessage"

    def _init(self, *args, **kwargs):
        super()._init(*args, **kwargs)
        self.text_above = self.body
        self.text_below = self.comment


    @property
    def html_text(self):
        return f'<span class="postmessage_body">{self.body}</span> <span class="postmessage_comment">{self.comment}</span>'
        

class Action(ProtocolStep):
    yaml_tag = '!action'
    type = "action"
    html_template = """<div class="{{ this.type }}" style="grid-column-start: {{ this.party.annexid }}; grid-row-start: {{ this.line + 1}};">
    {{ this.label }}
    </div>"""

    def _init(self, *args, **kwargs):
        super()._init(*args, **kwargs)
        self.node_name = self.create_affecting_node_name()

    def tikz(self):
        pos = self.get_pos(self.party.column, self.line)
        text = self.tex_id + self.contour(self.label)
        out = fr"""\node[annex_action,name={self.node_name}{self.tikz_extra_style}] at ({pos}) {{{text}}};"""
        return out

    @property
    def height(self):
        h = 1 + 2 * len(self.label.split("\\\\"))
        return f"{h}ex", "center"

    
class ScriptAction(Action):
    yaml_tag = '!script-action'
    data = ""
    label = ""
    id_above = False

    def _init(self, *args, **kwargs):
        self.party = self.src
        super()._init(*args, **kwargs)
    
    def tikz_arrows(self):
        direction = "east" if self.src.column < self.dest.column else "west"
        src = self.get_pos(self.src.column, self.line)
        dest = self.get_pos(self.dest.column, self.line)
        self.text_above = self.data
        rev = "_reversed" if getattr(self, 'reversed', False) else ''
        return fr"""%% draw script action arrow
        \draw[annex_script_action_arrow{rev}{self.tikz_extra_style}] ({self.node_name}.{direction}) to  {self.tikz_above} ({dest});"""

    @property
    def height(self):
        return "4ex", "center"
    
    @property
    def affected_parties(self):
        yield self.party
        yield self.src
        yield self.dest


class EndParty(ProtocolStep):
    yaml_tag = '!end-party'
    skip_number = True
    type = 'end_party'
    endsparty = True
    html_template = """
    <div class="{{ this.type }}" style="grid-column-start: {{ this.party.annexid }}; grid-row-start: {{ this.line + 1}};">
    {{ this.party.name }}
    </div>
    """

    def _init(self, *args, **kwargs):
        super()._init(*args, **kwargs)
        self.node_name = self.create_affecting_node_name()
    
    def tikz(self):
        pos = self.get_pos(self.party.column, self.line)
        text = self.party.name
        out = fr"""\node[name={self.node_name},annex_{self.type}_box,{self.party.style}] at ({pos}) {{{text}}};"""
        return out

    @property
    def height(self):
        return "5ex", "center"


class StartParty(EndParty):
    yaml_tag = '!start-party'
    skip_number = True
    type = 'start_party'
    endsparty = False
    startsparty = True
    lifeline_segments = []
    html_template = EndParty.html_template + """{% for start, end, style in this.lifeline_segments %}
    <div class="{{ style }}" style="grid-column-start: {{ this.party.column + 2 }}; grid-row-start: {{ (start // 2) + 2 }}; grid-row-end: {{ (end // 2) + 1 }};"></div>
    {% endfor %}"""

    def tikz_arrows(self):
        # lifeline_segments contains tuples (doublelinestart, doublelineend, style)
        out = ""
        for segment in self.lifeline_segments:
            if segment[0] % 2 == 1:
                node_above = self.get_pos(self.party.column, segment[0] // 2)
                node_below = self.get_pos(self.party.column, segment[0] // 2 + 1)
                out += fr"""\node[inner sep=0] ({node_above}-half) at ($({node_above})!0.5!({node_below})$) {{}};"""
                src = fr"""{node_above}-half"""
            else:
                src = self.get_pos(self.party.column, segment[0] // 2)
            if segment[1] % 2 == 1:
                node_above = self.get_pos(self.party.column, segment[1] // 2)
                node_below = self.get_pos(self.party.column, segment[1] // 2 + 1)
                out += fr"""\node[inner sep=0] ({node_above}-half) at ($({node_above})!0.5!({node_below})$) {{}};"""
                dest = fr"""{node_above}-half"""
            else:
                dest = self.get_pos(self.party.column, segment[1] // 2)
            out += fr"""\draw[{segment[2]}] ({src}) -- ({dest});"""
        return out



class DummyParty(ProtocolStep):
    yaml_tag = '!dummy-party'
    skip_number = True
    dummyparty = True

    def _init(self, *args, **kwargs):
        super()._init(*args, **kwargs)
        self.node_name = self.create_affecting_node_name()
    
#    def tikz(self):
#        pos = self.get_pos(self.party.column, self.line)
#        text = self.party.name
#        out = fr"""\node[name={self.node_name},annex_{self.type}_box,{self.party.style}] at ({pos}) {{{text}}};"""
#        return out
#
#    @property
#    def height(self):
#        return "5ex", "center"


class OpenWindowStartParty(StartParty):
    yaml_tag = '!open-window-start-party'
    id_above = True
    skip_number = False

    def _init(self, *args, **kwargs):
        super()._init(*args, **kwargs)
        self.party = self.dest
    
    def tikz_arrows(self):
        direction = "east" if self.src.column > self.dest.column else "west"
        src = self.get_pos(self.src.column, self.line)
        self.text_above = "open"
        out = fr"""%% draw open window arrow
        \draw[annex_open_window_start_party_arrow{self.tikz_extra_style}] ({src}) to  {self.tikz_above} ({self.node_name}.{direction});"""
        out += super().tikz_arrows()
        return out
    
    @property
    def height(self):
        return "6ex", "center,yshift=1ex"
    
    @property
    def affected_parties(self):
        yield self.src
        yield self.dest


class CloseWindowEndParty(EndParty):
    yaml_tag = '!close-window-end-party'
    id_above = True
    skip_number = False

    def _init(self, *args, **kwargs):
        super()._init(*args, **kwargs)
        self.party = self.dest
    
    def tikz_arrows(self):
        direction = "east" if self.src.column > self.dest.column else "west"
        src = self.get_pos(self.src.column, self.line)
        self.text_above = "close"
        out = fr"""%% draw close window arrow
        \draw[annex_close_window_end_party_arrow{self.tikz_extra_style}] ({src}) to  {self.tikz_above} ({self.node_name}.{direction});"""
        out += super().tikz_arrows()
        return out
    
    @property
    def height(self):
        return "6ex", "center,yshift=1ex"
    
    @property
    def affected_parties(self):
        yield self.src
        yield self.dest

