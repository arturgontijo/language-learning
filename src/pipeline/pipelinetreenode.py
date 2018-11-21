from typing import Dict, List, Any, Union, Callable

__all__ = ['PipelineTreeNode2']


class PipelineTreeNode2:
    """

    Pipeline execution tree node

    """
    roots = list()
    static_components = dict()

    def __init__(self,
                 seq_no: int,
                 name: str,
                 parameters: Dict[str, Any],
                 environment: Union[Dict[str, Any], None]=None,
                 parent=None):
        """

        :param seq_no:          Hierarchy level number;
        :param name:            Component name;
        :param parameters:      Configuration parameters
        :param environment:     Environment variables dictionary;
        :param parent:          Parent node reference.
        """
        if parent is None:
            self.roots.append(self)

        self.seq_no: int = seq_no
        self._component_name: str = name
        self._parameters: Dict[str, Any] = {} if parameters is None else parameters
        self._environment: Dict[str, Any] = {} if environment is None else environment
        self._siblings: List[PipelineTreeNode2] = []
        self._parent: Union[None, PipelineTreeNode2] = parent

        if self._parent is not None:
            self._parent.add_sibling(self)

    @staticmethod
    def free_static_components():
        for o in PipelineTreeNode2.static_components.values():
            if o is not None:
                del o

        PipelineTreeNode2.static_components = dict()

    @staticmethod
    def traverse(job: Callable, node = None) -> None:
        """

        Traverse pipeline tree executing the job

        :param job:         Function/method to execute for each node.
        :param node:        Node to start from
        :return:            None
        """
        if node is None:
            return None

        if job is not None:
            try:
                job(node)
            except Exception as err:
                print("Error: " + str(err))
                return None

        for sibling in node._siblings:
                PipelineTreeNode2.traverse(job, sibling)

    @staticmethod
    def traverse_all(job: Callable) -> None:
        """

        Traverse all execution paths of pipeline tree

        :param job:         Function/method to execute for each node.
        :return:            None
        """
        for i, root in enumerate(PipelineTreeNode2.roots, 0):
            print("Execution path: " + str(i))
            PipelineTreeNode2.traverse(job, root)

    @staticmethod
    def print_node(parameters: dict, environment: dict):
        print(parameters)

    def add_sibling(self, node) -> None:
        """

        Add sibling to pipeline tree

        :param node:    Sibling node to add.
        :return:        None
        """
        self._siblings.append(node)
