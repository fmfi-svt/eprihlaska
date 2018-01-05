import pdfkit
class HeadlessPdfKit(pdfkit.PDFKit):
    def command(self, path=None):
        return ['xvfb-run', '--'] + super().command(path)


def generate_pdf(rendered, options=None):
    rendered = rendered.replace('src="//', 'src="http://')
    rendered = rendered.replace('href="//', 'href="http://')
    pdf = HeadlessPdfKit(rendered, 'string',
                         options=options).to_pdf(False)
    return pdf

