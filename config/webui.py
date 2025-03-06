from IPython import get_ipython
from IPython.display import display, HTML
import utils
import html


CSS = utils.load_file('style.css')


def show_result(result, shell = get_ipython()) -> None:
    display(result)

def show_error(exception: Exception, shell = get_ipython()) -> None:
    # shell.showtraceback((type(exception), exception, exception.__traceback__))
    
    name = type(exception).__name__
    message = str(exception.args[0]) if exception.args else ''
    description = message.splitlines()[0]

    traceback = message.splitlines()[1:]
    traceback = '\n' + '\n'.join(traceback)
    traceback = html.escape(traceback)

    html_code = f'''
    <style>{CSS}</style>

    <div class="box">
        <div class="messagebox">
            <div class="icon">
                <i class="fas fa-exclamation-triangle"></i>
                <br>
                Insert AI name here 
            </div>
            <div class="message">
                <b class="title">{name}: {description}</b>
                <br>
                <pre class="code">{traceback}</pre>
            </div>
        </div>
    </div>
    '''

    display(HTML(html_code))

