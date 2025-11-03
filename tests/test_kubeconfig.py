import yaml
import os
import unittest

class TestKubeconfig(unittest.TestCase):
    def test_kubeconfig_structure(self):
        """Test that kubeconfig has the basic required structure"""
        kubeconfig_path = os.path.join(os.path.dirname(__file__), '..', 'kubeconfig-jenkins.yaml')
        
        with open(kubeconfig_path, 'r') as f:
            config = yaml.safe_load(f)

        self.assertIn('apiVersion', config)
        self.assertIn('clusters', config)
        self.assertIn('contexts', config)
        self.assertIn('users', config)
        self.assertIn('current-context', config)
        self.assertIn('kind', config)

        self.assertEqual(config['kind'], 'Config')

        self.assertGreater(len(config['clusters']), 0)

        self.assertGreater(len(config['users']), 0)

        self.assertGreater(len(config['contexts']), 0)
        
    def test_cluster_config(self):
        """Test cluster configuration structure"""
        kubeconfig_path = os.path.join(os.path.dirname(__file__), '..', 'kubeconfig-jenkins.yaml')
        
        with open(kubeconfig_path, 'r') as f:
            config = yaml.safe_load(f)
            
        cluster = config['clusters'][0]['cluster']

        self.assertIn('server', cluster)

        self.assertIn('certificate-authority-data', cluster)
        
    def test_user_config(self):
        """Test user configuration structure"""
        kubeconfig_path = os.path.join(os.path.dirname(__file__), '..', 'kubeconfig-jenkins.yaml')
        
        with open(kubeconfig_path, 'r') as f:
            config = yaml.safe_load(f)
            
        user = config['users'][0]['user']

        auth_methods = ['token', 'client-certificate-data', 'username', 'exec']
        self.assertTrue(any(method in user for method in auth_methods), 
                       "No authentication method found in user config")

if __name__ == '__main__':
    unittest.main()