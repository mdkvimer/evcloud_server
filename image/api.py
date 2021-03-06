#coding=utf-8
from datetime import datetime

from django.contrib.auth.models import User

from api.error import Error
from api.error import ERR_DISK_INIT
from api.error import ERR_DISK_ARCHIVE
from api.error import ERR_CEPH_ID
from api.error import ERR_IMAGE_INFO
from api.error import ERR_IMAGE_CEPHHOST
from api.error import ERR_IMAGE_CEPHPOOL

from storage.api import StorageAPI

from .manager import ImageManager




class ImageAPI(object):
    def __init__(self, manager=None, storage_api=None):
        if manager:
            self.manager = manager
        else:
            self.manager = ImageManager()
        if storage_api:
            self.storage_api = storage_api
        else:
            self.storage_api = StorageAPI()

    def _valid_diskname(self, disk_name):
        try:
            disk_name = str(disk_name)
        except:
            return False
        if len(disk_name) <= 0:
            return False
        return True

    def init_disk(self, image_id, disk_name):
        '''初始化磁盘'''
        image = self.manager.get_image_by_id(image_id)
        if not self._valid_diskname(disk_name):
            raise Error(ERR_DISK_NAME)
        return self.storage_api.clone(image.cephpool_id, image.snap, disk_name)

    def rm_disk(self, image_id, disk_name):
        image = self.manager.get_image_by_id(image_id)
        if not self._valid_diskname(disk_name):
            raise Error(ERR_DISK_NAME)
        return self.storage_api.rm(image.cephpool_id, disk_name)

    def archive_disk(self, image_id, disk_name, archive_disk_name=None,cephpool_id=None):
        if archive_disk_name == None:
            archive_disk_name = 'x_'+datetime.now().strftime("%Y%m%d%H%M%S")+'_'+str(disk_name)
            #archive_disk_name = 'x_'+datetime.now().strftime("%Y%m%d%H%M%S%f")+'_'+str(disk_name)
        else:
            if not self._valid_diskname(disk_name):
                raise Error(ERR_DISK_NAME)
        if not cephpool_id:
            image = self.manager.get_image_by_id(image_id)
            cephpool_id = image.cephpool_id
        if self.storage_api.mv(cephpool_id, disk_name, archive_disk_name):
            return archive_disk_name
        return False

    def disk_exists(self, image_id, disk_name,cephpool_id=None):
        if not cephpool_id:
            image = self.manager.get_image_by_id(image_id)
            cephpool_id = image.cephpool_id
        return self.storage_api.exists(cephpool_id, disk_name)

    def restore_disk(self, image_id, archive_disk_name):
        try:
            disk_name = archive_disk_name[2:38]
        except:
            raise Error(ERR_DISK_NAME)
        if not self._valid_diskname(disk_name):
            raise Error(ERR_DISK_NAME)
        image = self.manager.get_image_by_id(image_id)
        if self.storage_api.mv(image.cephpool_id, archive_disk_name, disk_name):
            return True
        return False        

    def get_image_info_by_id(self, image_id):
        '''根据镜像ID获取镜像相关的信息， 返回数据格式： {
                    'image_snap': *******,
                    'image_name': *******,
                    'image_version': ***,
                    'ceph_id': *,
                    'ceph_host': *.*.*.*,
                    'ceph_port': ****,
                    'ceph_uuid': ************************,
                    'ceph_pool': ******,
                    'ceph_username': *****

                }
        '''
        res = self.manager.get_image_info(image_id)
        if not res:
            raise Error(ERR_IMAGE_INFO)
        return res

    def get_xml_tpl(self, image_id):
        image = self.manager.get_image_by_id(image_id)
        return image.xml

    def get_image_by_id(self, image_id):
        return self.manager.get_image_by_id(image_id)

    def get_image_list_by_pool_id(self, pool_id, enable=None):
        return self.manager.get_image_list_by_pool_id(pool_id, enable)

    def get_image_type_list(self):
        return self.manager.get_image_type_list()

