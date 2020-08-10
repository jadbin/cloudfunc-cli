# coding=utf-8

from cloudfunc import cloud_class, cloud_func


@cloud_class
class ExampleCloudClass:

    @cloud_func('hello_world')
    def hello_world(self):
        """
        Write the instruction to use this cloud function here.
        If the name of the cloud function is not set, we will use the definition name instead.
        """
        return 'Hello World!'
