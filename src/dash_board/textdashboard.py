import sys
from ..common.absclient import AbstractDashboardClient, DashboardError, AbstractPipelineComponent
from ..common.cliutils import handle_path_string

__all__ = ['TextFileDashboard', 'CONF_ROW_KEY', 'CONF_ROW_IND', 'CONF_COL_KEY', 'CONF_COL_IND', 'CONF_VAL_KEYS',
           'CONF_ROW_COUNT', 'CONF_COL_COUNT', 'CONF_FILE_PATH', 'CONF_COL_HEADERS']

CONF_ROW_KEY = "row_key"
CONF_ROW_IND = "row_indexes"
CONF_COL_KEY = "col_key"
CONF_COL_IND = "col_indexes"
CONF_VAL_KEYS = "value_keys"
CONF_ROW_COUNT = "row_count"
CONF_COL_COUNT = "col_count"
CONF_FILE_PATH = "file_path"
CONF_COL_HEADERS = "col_headers"

class TextFileDashboard(AbstractDashboardClient):
    """
    Class which implements text file serialization.
        Exceptions: IndexError, ValueError
    """
    def __init__(self, config: dict):

        self.check_config(self)

        self._path = handle_path_string(config[CONF_FILE_PATH])
        self._row_count = config[CONF_ROW_COUNT] + len(config.get(CONF_COL_HEADERS, []))
        self._col_count = config[CONF_COL_COUNT]
        self._dashboard = [list() for r in range(0, self._row_count)]

        self.alloc_dashboard()
        self._set_headers(config)

    def alloc_dashboard(self):
        """ Allocate dashboard """
        for row in self._dashboard:
            for i in range(0, self._col_count):
                row.append(None)

    def _set_headers(self, config: dict) -> None:
        """ Set column headers """
        headers = config.get(CONF_COL_HEADERS, None)

        if headers is not None:
            for row in range(0, len(headers)):
                for col in range(0, self._col_count):
                    self._dashboard[row][col] = headers[row][col]["title"]

    @staticmethod
    def check_config(config) -> bool:
        return True

    def set_row_names(self, names: list) -> None:
        """ Set name for each row """
        size = len(names)

        if size != self._row_count:
            raise ValueError("'names' list size does not match the number of rows allocated")

        values = [i for i in range(size)]
        self._row_names = dict(zip(names, values))

    def set_col_names(self, names: list) -> None:
        """ Set name for each column. """
        size = len(names)

        if size != self._col_count:
            raise ValueError("'names' list size does not match the number of columns allocated")

        values = [i for i in range(size)]
        self._col_names = dict(zip(names, values))

    def _get_row_index(self, row_name: str) -> int:
        """ Get row index by name """
        if not hasattr(self, "_row_names"):
            raise DashboardError("row names are not set")

        return self._row_names[row_name]

    def _get_col_index(self, col_name: str) -> int:
        """ Get column index by name """
        if not hasattr(self, "_col_names"):
            raise DashboardError("column names are not set")

        return self._col_names[col_name]

    def set_cell_by_indexes(self, row_index: int, col_index: int, value:object) -> None:
        """ Set cell value by row and column indexes. """
        self._dashboard[row_index][col_index] = value

    def set_cell_by_names(self, row_name: str, col_name: str, value:object) -> None:
        """ Set cell value by row and column names. """
        self._dashboard[self._get_row_index(row_name)][self._get_col_index(col_name)] = value

    def _fill_empty_cells(self) -> None:
        """ Replace None with text string """
        for row in range(0, self._row_count):
            for col in range(0, self._col_count):
                if self._dashboard[row][col] is None:
                    self._dashboard[row][col] = "N/A"
                else:
                    self._dashboard[row][col] = str(self._dashboard[row][col])


    def update_dashboard(self) -> None:

        try:
            self._fill_empty_cells()

            with open(self._path, "w") as file:
                print(self.get_text(), file=file)

        except IOError as err:
            print("IOError: " + str(err))


    def get_text(self) -> str:
        """ Return dashboard as text string """
        text = ""

        for row in self._dashboard:
            text += '\t'.join(row) + "\n"

        return text


# class HTMLFileDashboard(TextFileDashboard):
#
#     def __init__(self, cfg_man: AbstractConfigClient):
#         super().__init__(cfg_man)
#
#     def update_dashboard(self):
#
#         # Return if dashboard is not configured.
#         if self._config is None:
#             return
#
#         try:
#             self._fill_empty_cells()
#
#             with open(self._path, "w") as file:
#
#                 print("<html><head>!!!</head><body><table>", file=file)
#
#                 for row in self._dashboard:
#                     print("<tr><td>" + "</td><td>".join(row) + "</td></tr>", file=file)
#
#                 print("</table></body></html>", file=file)
#
#         except IOError as err:
#             print("IOError: " + str(err))


class TextFileDashboardComponent(AbstractPipelineComponent):

    def __init__(self, **kwargs):
        self._board = TextFileDashboard(kwargs)

    def __exit__(self):
        print("__exit__", file=sys.stderr)
        self._board.update_dashboard()

    def __del__(self):
        print("__del__", file=sys.stderr)
        self._board.update_dashboard()

    def set(self, **kwargs):
        try:
            row = int(kwargs["row"])
            col = int(kwargs["col"])
            val = kwargs["val"]
            val = str(val).format(**kwargs)

            self._board.set_cell_by_indexes(row, col, val)

        except Exception as err:
            print(str(err))

    def validate_parameters(self, **kwargs) -> bool:
        return True

    def run(self, **kwargs) -> dict:
        return {}
