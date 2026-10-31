import json
import os

from kivy.app import App
from kivy.animation import Animation
from kivy.clock import Clock
from kivy.core.clipboard import Clipboard
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.utils import get_color_from_hex
from kivy.graphics import Color, Rectangle
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup


ARQUIVO = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "volumes.json"
)

LOJAS_INICIAIS = [
    {"nome": "AC1", "referencia": ""},
    {"nome": "MAT", "referencia": ""},
    {"nome": "SM", "referencia": ""},
    {"nome": "SJ", "referencia": ""},
    {"nome": "DIV", "referencia": ""},
    {"nome": "EF", "referencia": ""},
    {"nome": "DS", "referencia": ""},
    {"nome": "AC2", "referencia": ""},
    {"nome": "SDP", "referencia": ""},
    {"nome": "CARMINHA", "referencia": ""}
]

FUNDO = "#10141D"
CARTAO = "#1B2332"
VERDE = "#20C997"
AZUL = "#3478F6"
VERMELHO = "#E05260"
BRANCO = "#FFFFFF"
CINZA = "#AAB4C5"


class Botao(Button):
    def __init__(self, cor=CARTAO, **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ""
        self.background_down = ""
        self.background_color = get_color_from_hex(cor)
        self.color = get_color_from_hex(BRANCO)
        self.font_size = dp(15)
        self.bold = True
        self.halign = "center"
        self.valign = "middle"


class ControleVolumes(App):

    def build(self):
        self.title = "RFH1 - Controle de Volumes"

        # Mantém a barra de status do Android visível.
        Window.fullscreen = False
        Window.clearcolor = get_color_from_hex(FUNDO)
        Window.softinput_mode = "pan"

        self.lojas = []
        self.selecionada = None
        self.botoes = {}

        self.carregar_dados()

        raiz = BoxLayout(
            orientation="vertical",
            padding=[dp(12), dp(12), dp(12), dp(12)],
            spacing=dp(6)
        )

        # Fundo do aplicativo.
        with raiz.canvas.before:
            Color(*get_color_from_hex(FUNDO))
            self.fundo = Rectangle(
                pos=raiz.pos,
                size=raiz.size
            )

        raiz.bind(
            pos=self.atualizar_fundo,
            size=self.atualizar_fundo
        )

        titulo = Label(
            text="[b]CONTROLE DE VOLUMES[/b]",
            markup=True,
            font_size=dp(20),
            color=get_color_from_hex(BRANCO),
            size_hint_y=None,
            height=dp(36)
        )
        raiz.add_widget(titulo)

        self.total_label = Label(
            text="TOTAL GERAL: 0",
            font_size=dp(21),
            bold=True,
            color=get_color_from_hex(VERDE),
            size_hint_y=None,
            height=dp(38)
        )
        raiz.add_widget(self.total_label)

        self.selecao_label = Label(
            text="Toque em uma loja para contar",
            font_size=dp(13),
            color=get_color_from_hex(CINZA),
            size_hint_y=None,
            height=dp(23)
        )
        raiz.add_widget(self.selecao_label)

        self.lista = GridLayout(
            cols=1,
            spacing=dp(6),
            padding=(0, dp(3)),
            size_hint_y=None
        )
        self.lista.bind(
            minimum_height=self.lista.setter("height")
        )

        rolagem = ScrollView(
            do_scroll_x=False,
            bar_width=dp(4),
            scroll_type=["content", "bars"]
        )
        rolagem.add_widget(self.lista)
        raiz.add_widget(rolagem)

        linha1 = GridLayout(
            cols=2,
            spacing=dp(8),
            size_hint_y=None,
            height=dp(46)
        )

        btn_diminuir = Botao(
            text="− DIMINUIR",
            cor=VERMELHO
        )
        btn_diminuir.bind(on_release=self.diminuir)

        btn_copiar = Botao(
            text="COPIAR CONTAGEM",
            cor=AZUL,
            font_size=dp(13)
        )
        btn_copiar.bind(on_release=self.copiar)

        linha1.add_widget(btn_diminuir)
        linha1.add_widget(btn_copiar)
        raiz.add_widget(linha1)

        linha2 = GridLayout(
            cols=2,
            spacing=dp(8),
            size_hint_y=None,
            height=dp(44)
        )

        btn_adicionar = Botao(
            text="+ NOVA LOJA",
            cor="#6655CC",
            font_size=dp(13)
        )
        btn_adicionar.bind(
            on_release=self.popup_nova_loja
        )

        btn_zerar = Botao(
            text="ZERAR TUDO",
            cor="#414B5E",
            font_size=dp(13)
        )
        btn_zerar.bind(on_release=self.popup_zerar)

        linha2.add_widget(btn_adicionar)
        linha2.add_widget(btn_zerar)
        raiz.add_widget(linha2)

        btn_apagar = Botao(
            text="APAGAR LOJA",
            cor=VERMELHO,
            size_hint_y=None,
            height=dp(44)
        )
        btn_apagar.bind(
            on_release=self.popup_apagar_loja
        )
        raiz.add_widget(btn_apagar)

        self.atualizar_lista()
        return raiz

    def atualizar_fundo(self, instancia, valor):
        self.fundo.pos = instancia.pos
        self.fundo.size = instancia.size

    def carregar_dados(self):
        if os.path.exists(ARQUIVO):
            try:
                with open(
                    ARQUIVO, "r", encoding="utf-8"
                ) as arquivo:
                    dados = json.load(arquivo)

                self.lojas = dados.get("lojas", [])

                for loja in self.lojas:
                    loja.setdefault("referencia", "")
                    loja.setdefault("quantidade", 0)

                return

            except (OSError, ValueError, TypeError):
                pass

        self.lojas = [
            {
                "nome": loja["nome"],
                "referencia": loja["referencia"],
                "quantidade": 0
            }
            for loja in LOJAS_INICIAIS
        ]

    def salvar_dados(self):
        try:
            temporario = ARQUIVO + ".tmp"

            with open(
                temporario, "w", encoding="utf-8"
            ) as arquivo:
                json.dump(
                    {"lojas": self.lojas},
                    arquivo,
                    ensure_ascii=False,
                    indent=2
                )

            os.replace(temporario, ARQUIVO)

        except OSError:
            self.aviso(
                "Erro",
                "Não foi possível salvar os dados."
            )

    def atualizar_lista(self):
        self.lista.clear_widgets()
        self.botoes = {}

        for loja in self.lojas:
            nome = loja["nome"]
            quantidade = loja.get("quantidade", 0)
            referencia = loja.get("referencia", "")

            texto = f"{nome}   |   {quantidade} VOLUMES"

            if referencia:
                texto += f"\nReferência: {referencia}"

            botao = Botao(
                text=texto,
                cor=CARTAO,
                size_hint_y=None,
                height=dp(60),
                font_size=dp(14)
            )

            botao.bind(
                on_release=lambda btn, item=loja:
                self.adicionar(item, btn)
            )

            self.botoes[nome] = botao
            self.lista.add_widget(botao)

        self.atualizar_total()

    def adicionar(self, loja, botao):
        loja["quantidade"] = loja.get("quantidade", 0) + 1
        self.selecionada = loja

        self.selecao_label.text = (
            "Selecionada: " + loja["nome"]
        )

        Animation.cancel_all(botao)
        botao.background_color = get_color_from_hex(VERDE)

        animacao = Animation(
            background_color=get_color_from_hex(CARTAO),
            duration=0.25
        )

        Clock.schedule_once(
            lambda dt: animacao.start(botao),
            0.12
        )

        botao.text = (
            f'{loja["nome"]}   |   '
            f'{loja["quantidade"]} VOLUMES'
        )

        if loja.get("referencia"):
            botao.text += (
                f'\nReferência: {loja["referencia"]}'
            )

        self.atualizar_total()
        self.salvar_dados()

    def atualizar_total(self):
        total = sum(
            loja.get("quantidade", 0)
            for loja in self.lojas
        )
        self.total_label.text = f"TOTAL GERAL: {total}"

    def diminuir(self, botao):
        if self.selecionada is None:
            self.aviso(
                "Atenção",
                "Primeiro toque na loja desejada."
            )
            return

        if self.selecionada.get("quantidade", 0) > 0:
            self.selecionada["quantidade"] -= 1
            self.atualizar_lista()
            self.salvar_dados()
        else:
            self.aviso(
                "Atenção",
                "Essa loja já está zerada."
            )

    def copiar(self, botao):
        linhas = []

        for loja in self.lojas:
            quantidade = loja.get("quantidade", 0)

            if quantidade > 0:
                linha = f'{loja["nome"]}: {quantidade}'

                if loja.get("referencia"):
                    linha += (
                        f' | Ref.: {loja["referencia"]}'
                    )

                linhas.append(linha)

        total = sum(
            loja.get("quantidade", 0)
            for loja in self.lojas
        )

        linhas.append("")
        linhas.append(f"TOTAL GERAL: {total}")

        Clipboard.copy("\n".join(linhas))
        self.aviso(
            "Copiado!",
            "A contagem foi copiada."
        )

    def popup_nova_loja(self, botao):
        caixa = BoxLayout(
            orientation="vertical",
            padding=dp(12),
            spacing=dp(10)
        )

        nome = TextInput(
            hint_text="Nome da loja",
            multiline=False,
            size_hint_y=None,
            height=dp(48)
        )

        referencia = TextInput(
            hint_text="Referência (opcional)",
            multiline=False,
            size_hint_y=None,
            height=dp(48)
        )

        caixa.add_widget(nome)
        caixa.add_widget(referencia)

        salvar = Botao(
            text="CADASTRAR LOJA",
            cor=AZUL,
            size_hint_y=None,
            height=dp(48)
        )
        caixa.add_widget(salvar)

        popup = Popup(
            title="Nova loja",
            content=caixa,
            size_hint=(0.9, 0.42)
        )

        def cadastrar(instancia):
            nome_loja = nome.text.strip()
            ref = referencia.text.strip()

            if not nome_loja:
                self.aviso(
                    "Atenção",
                    "Digite o nome da loja."
                )
                return

            if any(
                item["nome"].casefold() == nome_loja.casefold()
                for item in self.lojas
            ):
                self.aviso(
                    "Atenção",
                    "Essa loja já está cadastrada."
                )
                return

            self.lojas.append({
                "nome": nome_loja,
                "referencia": ref,
                "quantidade": 0
            })

            self.atualizar_lista()
            self.salvar_dados()
            popup.dismiss()

        salvar.bind(on_release=cadastrar)
        popup.open()

    def popup_apagar_loja(self, botao):
        if not self.lojas:
            self.aviso(
                "Atenção",
                "Não existem lojas cadastradas."
            )
            return

        caixa = BoxLayout(
            orientation="vertical",
            padding=dp(12),
            spacing=dp(8)
        )

        caixa.add_widget(
            Label(
                text="Escolha a loja que deseja apagar:",
                size_hint_y=None,
                height=dp(40)
            )
        )

        rolagem = ScrollView()

        lista = GridLayout(
            cols=1,
            spacing=dp(6),
            size_hint_y=None
        )
        lista.bind(
            minimum_height=lista.setter("height")
        )

        popup = Popup(
            title="Apagar loja",
            content=caixa,
            size_hint=(0.9, 0.75)
        )

        def selecionar(loja):
            popup.dismiss()
            self.confirmar_apagar_loja(loja)

        for loja in self.lojas:
            botao_loja = Botao(
                text=loja["nome"],
                cor=VERMELHO,
                size_hint_y=None,
                height=dp(50)
            )

            botao_loja.bind(
                on_release=lambda instancia, item=loja:
                selecionar(item)
            )
            lista.add_widget(botao_loja)

        rolagem.add_widget(lista)
        caixa.add_widget(rolagem)

        fechar = Botao(
            text="CANCELAR",
            cor=AZUL,
            size_hint_y=None,
            height=dp(45)
        )
        fechar.bind(
            on_release=lambda instancia: popup.dismiss()
        )

        caixa.add_widget(fechar)
        popup.open()

    def confirmar_apagar_loja(self, loja):
        caixa = BoxLayout(
            orientation="vertical",
            padding=dp(12),
            spacing=dp(12)
        )

        caixa.add_widget(
            Label(
                text=(
                    f'Deseja apagar a loja "{loja["nome"]}"?\n'
                    "A contagem dela também será excluída."
                ),
                halign="center"
            )
        )

        botoes = GridLayout(
            cols=2,
            spacing=dp(8),
            size_hint_y=None,
            height=dp(48)
        )

        popup = Popup(
            title="Confirmar exclusão",
            content=caixa,
            size_hint=(0.9, 0.35)
        )

        sim = Botao(text="APAGAR", cor=VERMELHO)
        nao = Botao(text="CANCELAR", cor=AZUL)

        def apagar(instancia):
            if loja in self.lojas:
                self.lojas.remove(loja)

                if self.selecionada is loja:
                    self.selecionada = None
                    self.selecao_label.text = (
                        "Toque em uma loja para contar"
                    )

                self.atualizar_lista()
                self.salvar_dados()

            popup.dismiss()
            self.aviso(
                "Loja excluída",
                f'A loja "{loja["nome"]}" foi apagada.'
            )

        sim.bind(on_release=apagar)
        nao.bind(
            on_release=lambda instancia: popup.dismiss()
        )

        botoes.add_widget(sim)
        botoes.add_widget(nao)
        caixa.add_widget(botoes)
        popup.open()

    def popup_zerar(self, botao):
        caixa = BoxLayout(
            orientation="vertical",
            padding=dp(12),
            spacing=dp(12)
        )

        caixa.add_widget(
            Label(
                text="Deseja zerar todas as contagens?"
            )
        )

        botoes = GridLayout(
            cols=2,
            spacing=dp(8),
            size_hint_y=None,
            height=dp(48)
        )

        popup = Popup(
            title="Confirmar",
            content=caixa,
            size_hint=(0.85, 0.3)
        )

        sim = Botao(
            text="SIM, ZERAR",
            cor=VERMELHO
        )
        nao = Botao(
            text="CANCELAR",
            cor=AZUL
        )

        def confirmar(instancia):
            for loja in self.lojas:
                loja["quantidade"] = 0

            self.selecionada = None
            self.selecao_label.text = (
                "Toque em uma loja para contar"
            )

            self.atualizar_lista()
            self.salvar_dados()
            popup.dismiss()

        sim.bind(on_release=confirmar)
        nao.bind(
            on_release=lambda instancia: popup.dismiss()
        )

        botoes.add_widget(sim)
        botoes.add_widget(nao)
        caixa.add_widget(botoes)
        popup.open()

    def aviso(self, titulo, mensagem):
        caixa = BoxLayout(
            orientation="vertical",
            padding=dp(12),
            spacing=dp(10)
        )

        caixa.add_widget(
            Label(
                text=mensagem,
                halign="center"
            )
        )

        fechar = Botao(
            text="OK",
            cor=AZUL,
            size_hint_y=None,
            height=dp(45)
        )
        caixa.add_widget(fechar)

        popup = Popup(
            title=titulo,
            content=caixa,
            size_hint=(0.85, 0.3)
        )

        fechar.bind(
            on_release=lambda instancia: popup.dismiss()
        )
        popup.open()


if __name__ == "__main__":
    ControleVolumes().run()
