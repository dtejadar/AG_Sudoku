from reactpy import component, html, hooks
import httpx  # Cliente HTTP para python

@component
def SudokuApp():
    size, set_size = hooks.use_state(0)
    board, set_board = hooks.use_state(None)
    solution, set_solution = hooks.use_state(None)
    history, set_history = hooks.use_state([])
    generations, set_generations = hooks.use_state("0")
    
    async def handle_change(event):
        new_size = int(event["target"]["value"])
        set_size(new_size)
        await generate_board(event, new_size)

    async def generate_board(event, selected_size):
        set_history([])
        set_solution(None)
        print(f"Generando tablero de tamaño {selected_size}...")
        async with httpx.AsyncClient() as client:
            response = await client.post("http://127.0.0.1:8001/api/generate_board", json={"size": selected_size})
            if response.status_code == 200:
                set_board(response.json()["board"])
                print(f"Tablero generado: {response.json()['board']}")
            else:
                print(f"Error: {response.status_code}")

    async def solve_sudoku(event):
        set_history([])
        set_solution(None)
        if(board is None): return
        async with httpx.AsyncClient() as client:
            response = await client.post("http://127.0.0.1:8001/api/solve_sudoku", json={"board": board})            
            if response.status_code == 200:
                set_solution(response.json()["solution"])
                set_history(response.json()["history"])
                set_generations(response.json()["generations"])
                print(f"Tablero solucionado")
            else:
                print(f"Error: {response.status_code}")

    return html.div({"class": "container-app"},
        [
            html.h1({"class": "main-title"},"Algoritmo Genético para Sudoku"),
            html.div({"class": "configuration-container"},
                [
                    html.label({"class": "form-label"}, "Tamaño del Sudoku"),
                    html.select(
                        {
                            "class": "form-select form-select-lg mb-3 ml-3",
                            "value": size,                            
                            "onchange": handle_change
                        },
                        html.option({"value": 0}, "Seleccione un tamaño"),
                        html.option({"value": 4}, "4x4"),
                        html.option({"value": 9}, "9x9")
                    ),                    
                    html.button({
                        "class": "btn btn-primary btn-m",
                        "type": "button",
                        "onclick": solve_sudoku
                    }, "Resolver Sudoku"),
                ]
            ),
            html.div(
                html.h2("Tablero Inicial"),
                html.table(
                    [html.tr([html.td(cell) for cell in row]) for row in (board or [])]
                ) if board else "No se ha generado un tablero aún."
            ),
            html.div(
                html.h2("Iteraciones de Tableros"),
                html.div(
                    {
                        "style": "display: flex; flex-wrap: wrap;"
                    },
                    [html.table(
                        [html.tr([html.td(cell) for cell in row]) for row in (iteration or [])]
                    ) for iteration in history]
                ),
                html.br() if history else "No hay iteraciones aún."
            ),
            html.div(
                html.h2("Tablero solución - " + generations + " Generaciones "),
                html.table(
                    [html.tr([html.td(cell) for cell in row]) for row in (solution or [])]
                ) if solution else "No se ha resuelto el Sudoku aún."
            ),
        ]
    )
